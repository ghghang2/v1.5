# Debug Breaking Error Message - Progress Tracker

## Task: Debug and resolve the APIError: "Invalid diff: now finding less tool calls!"

### Status: In Progress

### Current Progress:
1. Identified error location: `/content/nbchat/ui/conversation.py` line 165 in `_stream_response`
2. Error occurs during streaming response processing
3. Related to tool calls in the diff

### Next Steps:
1. Examine the conversation.py file
2. Look at the diff generation logic
3. Check recent changes that might have caused fewer tool calls
4. Review the OpenAI API requirements for diffs

### Blockers:
- None yet

### Notes:
- Error traceback shows issue in streaming response handling
- The error message "now finding less tool calls!" suggests a change in tool call generation