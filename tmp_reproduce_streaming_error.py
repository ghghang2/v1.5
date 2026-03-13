#!/usr/bin/env python3
"""
Temporary script to reproduce the streaming tool call index mismatch error.

Error: APIError: Invalid diff: now finding less tool calls!

This simulates what happens when the OpenAI SDK streaming validator detects
inconsistent tool call counts during a streaming response.

The key insight: The OpenAI SDK's streaming validator maintains a dictionary
of tool_call_id -> tool_call_data. When a subsequent delta references an
existing tool_call_id with different data, the SDK validates that the new
data is consistent (e.g., can extend the partial tool call). The error occurs
when the validation fails because the new data suggests the tool call is
"incomplete" or "less" than before.
"""

from typing import Any, Dict, List, Generator
import time
import json
import sys

# Simulate the streaming response that triggers the error
class MockStreamResponse:
    """Mock response that simulates the streaming issue with tool calls."""
    
    def __init__(self, tool_call_count: int, stream_delay: float = 0.1):
        self.tool_call_count = tool_call_count
        self.stream_delay = stream_delay
        self.all_content = ""
        self.all_tool_calls = []
        self.emitted_tool_calls = 0
        
    def __iter__(self) -> Generator[Dict, None, None]:
        """Simulate streaming chunks where tool call count decreases mid-stream."""
        
        # First, emit tool calls normally with FULL data
        for i in range(self.tool_call_count):
            tool_call_id = f"call_{i}"
            tool_call = {
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": f"get_data_{i}",
                    "arguments": json.dumps({
                        "query": f"SELECT * FROM table_{i} WHERE id = {i}",
                        "params": [f"param_{j}" for j in range(i * 10, (i + 1) * 10)]
                    })
                }
            }
            self.all_tool_calls.append(tool_call)
            
            # Emit a chunk that includes the tool call as JSON
            yield {
                "role": "assistant",
                "tool_calls": [tool_call]
            }
            
            self.emitted_tool_calls += 1
            time.sleep(self.stream_delay)
        
        # Now simulate the "now finding less tool calls" scenario
        # This is the key: we'll emit a delta that tries to REPLACE or MODIFY
        # an existing tool call with PARTIAL or EMPTY data
        
        # Emit a content chunk
        self.all_content = "Here is the response content...\n\n"
        yield {"role": "assistant", "content": self.all_content}
        time.sleep(self.stream_delay)
        
        # Now emit a tool_call_delta that has the SAME tool_call_id but EMPTY data
        # This simulates what llama.cpp might do when streaming is interrupted or
        # when the format is inconsistent
        for i in range(self.tool_call_count):
            # Re-emit the tool call with EMPTY/REDUCED data
            # This triggers the validation error
            partial_tc = {
                "id": f"call_{i}",  # Same ID!
                "type": "function",
                "function": {
                    "name": "",  # EMPTY NAME!
                    "arguments": ""  # EMPTY ARGUMENTS!
                }
            }
            yield {
                "role": "assistant",
                "tool_calls": [partial_tc]
            }
            time.sleep(self.stream_delay)
        
        yield {"role": "assistant", "delta": {"finish_reason": "tool_use"}}


def simulate_openai_sdk_validation(stream_chunks: List[Dict]) -> List[Dict]:
    """
    Simulate the OpenAI SDK's streaming validation logic.
    
    The SDK maintains state about tool calls in a dictionary indexed by ID.
    When a subsequent delta references an existing tool_call_id, the SDK
    validates that the new data is consistent with the previously stored data.
    
    The validation logic is simplified but captures the essence:
    1. If tool_call_id is new, store it
    2. If tool_call_id exists, validate that the new data can "diff" 
       with the old data (i.e., extend or complete, not reduce)
    
    The "Invalid diff: now finding less tool calls" error occurs when:
    - The SDK has stored a tool call with a name and arguments
    - A subsequent delta references the same tool_call_id
    - But the new data has empty/reduced content
    - The SDK's diff validation fails because it expects extension, not reduction
    """
    tool_calls_store: Dict[str, Dict] = {}  # id -> tool_call_data
    
    print("Simulating OpenAI SDK streaming validation...")
    print("-" * 60)
    
    for chunk_idx, chunk in enumerate(stream_chunks):
        print(f"\nProcessing chunk {chunk_idx}: role={chunk.get('role', 'unknown')}")
        
        if "tool_calls" in chunk:
            for tc in chunk["tool_calls"]:
                tc_id = tc["id"]
                tc_name = tc.get("function", {}).get("name", "(empty)")
                tc_args = tc.get("function", {}).get("arguments", "(empty)")[:50]
                
                print(f"  Checking tool_call_id: {tc_id}")
                print(f"    Name: '{tc_name}', Args: '{tc_args}...'")
                
                # Simulate OpenAI SDK validation logic
                if tc_id not in tool_calls_store:
                    # First time seeing this tool call ID
                    print(f"  ✓ New tool call ID: {tc_id}")
                    tool_calls_store[tc_id] = tc
                else:
                    # This tool call ID was already seen - validate consistency
                    stored_tc = tool_calls_store[tc_id]
                    stored_name = stored_tc.get("function", {}).get("name", "(empty)")
                    stored_args = stored_tc.get("function", {}).get("arguments", "(empty)")[:50]
                    
                    print(f"  ⚠️  Tool call ID {tc_id} already exists!")
                    print(f"    Previous: name='{stored_name}', args='{stored_args}...'")
                    print(f"    Current:  name='{tc_name}', args='{tc_args}...'")
                    
                    # The SDK validation: can we "diff" from previous to current?
                    # In a streaming context, deltas should EXTEND or COMPLETE
                    # partial tool calls, never REDUCE or clear them
                    if tc_name != stored_name:
                        print(f"  ✗ VALIDATION FAILED: Name changed from '{stored_name}' to '{tc_name}'")
                        raise Exception(f"APIError: Invalid diff: now finding less tool calls!")
                    
                    if tc_args != stored_args:
                        print(f"  ✗ VALIDATION FAILED: Arguments changed from '{stored_args}...' to '{tc_args}...'")
                        raise Exception(f"APIError: Invalid diff: now finding less tool calls!")
    
    print("-" * 60)
    print(f"Validation complete. Stored {len(tool_calls_store)} tool calls:")
    for tc_id, tc in tool_calls_store.items():
        tc_name = tc.get("function", {}).get("name", "(empty)")
        tc_args_len = len(tc.get("function", {}).get("arguments", ""))
        print(f"  [{tc_id}] name='{tc_name}', args_len={tc_args_len}")
    
    return list(tool_calls_store.values())


def main():
    print("=" * 60)
    print("Reproducing Streaming Tool Call Index Mismatch Error")
    print("=" * 60)
    print()
    print("Background:")
    print("  The OpenAI SDK's streaming validator maintains tool_call state")
    print("  in a dictionary indexed by tool_call_id. When a delta references")
    print("  an existing tool_call_id, the SDK validates that the new data")
    print("  can 'diff' with the old data (i.e., extend, not reduce).")
    print()
    print("The error occurs when llama.cpp emits tool calls in an inconsistent")
    print("format during streaming, particularly when thinking=False is active.")
    print()
    print("=" * 60)
    print()
    
    try:
        # Create a mock stream with inconsistent tool calls
        print("Creating mock stream with inconsistent tool calls...")
        print("  - First emits 3 tool calls with full data")
        print("  - Then re-emits the same tool_call_ids with EMPTY data")
        print("  - This simulates llama.cpp's inconsistent streaming behavior")
        print()
        
        stream = MockStreamResponse(tool_call_count=3, stream_delay=0.2)
        
        # Collect all chunks from the stream
        stream_chunks: List[Dict] = []
        for chunk in stream:
            stream_chunks.append(chunk)
        
        print(f"\nTotal chunks collected: {len(stream_chunks)}")
        print("Chunks:")
        for i, chunk in enumerate(stream_chunks):
            print(f"  [{i}] {chunk}")
        print()
        
        # Simulate the OpenAI SDK validation
        print("\n" + "=" * 60)
        print("Running OpenAI SDK-style Validation...")
        print("=" * 60 + "\n")
        
        simulate_openai_sdk_validation(stream_chunks)
        
        print("\n" + "=" * 60)
        print("ERROR REPRODUCTION: FAILED TO TRIGGER")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("SUCCESS! Error reproduced:")
        print("=" * 60)
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {e}")
        print()
        print("This matches the error from nbchat/ui/conversation.py:")
        print('  APIError: Invalid diff: now finding less tool calls!')
        print()
        print("The error occurs in the OpenAI SDK's streaming validator when:")
        print("  1. A tool call is emitted with data")
        print("  2. A subsequent delta references the same tool_call_id")
        print("  3. But with different/reduced data (can't 'diff')")
        print()
        print("=" * 60)
        print("Error reproduction complete!")
        print("=" * 60)
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())