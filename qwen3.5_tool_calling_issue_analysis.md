# Qwen3.5 9B Tool Calling Issue Analysis

## Problem Summary

For Qwen3.5 9B models (and other quantizations), tool calling works for the first tool call but fails on subsequent calls. The second tool call shows up in `reasoning_content`, but the `tool_calls` field in the delta chunk of the response stream is `None` (OpenAI standard).

## Root Cause Analysis

### 1. Chat Template Configuration Issue

The key finding is in the `run.py` file:

```python
"--chat-template-kwargs", '{"enable_thinking": true}',
```

According to the Unsloth documentation for Qwen3.5:

> "For Qwen3.5 0.8B, 2B, 4B and 9B, reasoning is disabled by default. To enable it, use: --chat-template-kwargs '{"enable_thinking":true}'"

However, this creates a conflict with tool calling. When `enable_thinking` is set to `true`, the model's chat template changes how it formats responses, particularly affecting how tool calls are structured in the streaming output.

### 2. Qwen3.5 Tool Calling Fix

The Unsloth documentation mentions:

> "Tool-calling improved following our chat template fixes. Fix is universal and applies to any Qwen3.5 format and any uploader."

This indicates that there were known issues with Qwen3.5 tool calling that were fixed in the chat template. The fix likely involves how the model handles the distinction between `reasoning_content` and `tool_calls` in the response.

### 3. The Specific Issue

When the model is configured with `enable_thinking: true`, it appears to:
1. Output the first tool call correctly in the `tool_calls` field
2. For subsequent tool calls, output the tool call information in `reasoning_content` instead of `tool_calls`

This suggests that the chat template is not properly separating reasoning/thinking content from tool call structures after the first tool call.

### 4. Evidence from the Code

In `conversation.py`, the `_stream_response` method handles both `reasoning_content` and `tool_calls`:

```python
if getattr(delta, "reasoning_content", None):
    reasoning_accum += delta.reasoning_content
    # ...

if delta.tool_calls:
    for tc in delta.tool_calls:
        # Process tool calls
```

The issue is that after the first tool call, the model starts putting tool call information in `reasoning_content` instead of `tool_calls`, causing the `tool_calls` field to be `None` in subsequent chunks.

## Solutions

### Option 1: Disable Thinking Mode for Tool Calling

For Qwen3.5 9B models, try disabling thinking mode:

```python
"--chat-template-kwargs", '{"enable_thinking": false}',
```

This should force the model to use the standard tool calling format without mixing reasoning content.

### Option 2: Update llama.cpp Chat Template

Ensure you're using the latest llama.cpp version that includes the Qwen3.5 chat template fixes mentioned in the Unsloth documentation. The fix was universal and applies to any Qwen3.5 format.

### Option 3: Use Different Model Quantization

The comment in `repo_config.yaml` notes:

```yaml
# MODEL_NAME: "unsloth/Qwen3.5-9B-GGUF:" #Q4_K_M, UD-Q5_K_XL, Q8_0(fails on tool calls...)
```

This suggests that Q8_0 quantization specifically fails on tool calls. Try using:
- Q4_K_M
- UD-Q5_K_XL
- UD-IQ3_XXS (currently in use)

### Option 4: Check llama.cpp Version

Ensure you're using the latest llama.cpp build that supports Qwen3.5 tool calling properly. The issue might be in how the server formats the streaming response.

## Recommended Action

1. **First, try disabling thinking mode** in `run.py`:
   ```python
   "--chat-template-kwargs", '{"enable_thinking": false}',
   ```

2. **If that doesn't work**, check if there's a newer version of the llama-server binary that includes the Qwen3.5 chat template fixes.

3. **Verify the model quantization** - ensure you're not using Q8_0 which is noted to fail on tool calls.

4. **Check the llama.cpp chat template** - ensure it's properly configured for Qwen3.5 tool calling format.

## Additional Context

From the Unsloth documentation:
- Qwen3.5 Small models (0.8B, 2B, 4B, 9B) disable reasoning by default
- Tool calling was improved following chat template fixes
- The fix is universal and applies to any Qwen3.5 format

This suggests the issue is likely in the chat template configuration rather than the model itself.

## Testing Steps

1. Change `enable_thinking` to `false` in `run.py`
2. Restart the llama-server
3. Test tool calling with a simple request that requires multiple tool calls
4. Monitor the streaming response to see if `tool_calls` field is populated correctly in all chunks

## Conclusion

The root cause is likely a conflict between the `enable_thinking` chat template parameter and the tool calling format in Qwen3.5. When thinking is enabled, the model mixes reasoning content with tool calls, causing subsequent tool calls to appear in `reasoning_content` instead of `tool_calls`. The fix is to either disable thinking mode or ensure the latest chat template fixes are applied.