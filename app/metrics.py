import requests
import streamlit as st

@st.cache_resource(ttl=5)
def get_llama_metrics(url: str) -> dict[str, str]:
    """Fetch Prometheus‑style metrics from the Llama‑Server endpoint.

    Parameters
    ----------
    url: str
        Full URL to the ``/metrics`` endpoint (e.g. ``http://localhost:8000/metrics``).

    Returns
    -------
    dict[str, str]
        Mapping of metric name to its string value.
    """
    resp = requests.get(url, timeout=2)
    resp.raise_for_status()
    metrics: dict[str, str] = {}
    for line in resp.text.splitlines():
        if line.startswith("#") or not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            metrics[parts[0]] = parts[1]
    return metrics
