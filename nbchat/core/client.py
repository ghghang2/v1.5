# from openai import OpenAI
# from .config import SERVER_URL
# def get_client() -> OpenAI:
#     """Return a client that talks to the local OpenAI‑compatible server."""
#     return OpenAI(base_url=f"{SERVER_URL}/v1", api_key="")
import logging
import time
from openai import OpenAI
from .config import SERVER_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Inference_Metrics")

class MetricsLoggingClient:
    """A wrapper around the OpenAI client to log metrics for both standard and streaming chat completions."""
    def __init__(self, client: OpenAI):
        self._client = client
        self.chat = self._ChatWrapper(client.chat)

    def __getattr__(self, name):
        # Delegate all other calls to the original client
        return getattr(self._client, name)

    class _ChatWrapper:
        def __init__(self, chat):
            self._chat = chat
            self.completions = self._CompletionsWrapper(chat.completions)

    class _CompletionsWrapper:
        def __init__(self, completions):
            self._completions = completions

        def _stream_generator(self, stream, start_time):
            """Internal generator to intercept stream chunks and log final metrics."""
            ttft = None
            usage = None
            
            for chunk in stream:
                # Capture Time to First Token (TTFT) on the very first chunk
                if ttft is None:
                    ttft = time.time() - start_time
                    logger.info(f"Metrics | Time to First Token (TTFT): {ttft:.3f}s")
                
                # Check if this chunk contains usage data
                if hasattr(chunk, 'usage') and chunk.usage is not None:
                    usage = chunk.usage
                    
                yield chunk
                
            total_time = time.time() - start_time
            
            # Log final usage once the stream is fully consumed
            if usage:
                logger.info(
                    f"Metrics | Total Stream Latency: {total_time:.2f}s | "
                    f"Prompt: {usage.prompt_tokens} | "
                    f"Completion: {usage.completion_tokens} | "
                    f"Total Tokens: {usage.total_tokens}"
                )
            else:
                logger.warning(f"Metrics | Total Stream Latency: {total_time:.2f}s | No usage data returned in stream.")

        def create(self, *args, **kwargs):
            is_streaming = kwargs.get("stream", False)
            
            # Instruct the server to send usage data in the final stream chunk
            if is_streaming and "stream_options" not in kwargs:
                kwargs["stream_options"] = {"include_usage": True}

            start_time = time.time()
            response = self._completions.create(*args, **kwargs)
            
            if is_streaming:
                # Return our intercepted generator instead of the raw stream
                return self._stream_generator(response, start_time)
            else:
                # Handle standard (non-streaming) responses
                latency = time.time() - start_time
                if hasattr(response, 'usage') and response.usage:
                    u = response.usage
                    logger.info(
                        f"Metrics | Latency: {latency:.2f}s | "
                        f"Prompt: {u.prompt_tokens} | "
                        f"Completion: {u.completion_tokens} | "
                        f"Total Tokens: {u.total_tokens}"
                    )
                return response

def get_client() -> MetricsLoggingClient:
    """Return a client that talks to the local server and logs metrics."""
    base_client = OpenAI(base_url=f"{SERVER_URL}/v1", api_key="sk-local")
    return MetricsLoggingClient(base_client)