import streamlit as st
from pathlib import Path
from app.metrics import get_llama_metrics

def display_metrics_panel() -> None:
    """Adds a sidebar expander to toggle and show Llama\u2011Server metrics.

    The panel reads the public metrics URL from ``tunnel_url.txt`` if it
    exists, otherwise falls back to ``http://localhost:8000``.  The URL
    should point to the ``/metrics`` endpoint.
    """
    base_url = "http://localhost:8000/metrics"
    try:
        metrics = get_llama_metrics(base_url)
        if metrics:
            for k, v in metrics.items():
                st.markdown(f"{k}: {v}")
        else:
            st.info("No metrics returned from server.")
    except Exception as exc:
        st.error(f"Error fetching metrics: {exc}")
