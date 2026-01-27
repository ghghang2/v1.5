#!/usr/bin/env python3
"""
app.py – Streamlit UI that talks to a local llama‑server and can push the repo
to GitHub.  The code is intentionally kept compact and free of syntax
issues while preserving all original behaviour.
"""

import json
from pathlib import Path

from git import InvalidGitRepositoryError, Repo
import streamlit as st
import streamlit.components.v1 as components

from app.config import DEFAULT_SYSTEM_PROMPT
from app.client import get_client
from app.tools import get_tools, TOOLS
from app.docs_extractor import extract


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def refresh_docs() -> str:
    """Run the extractor and return the Markdown content."""
    return extract().read_text(encoding="utf-8")


def is_repo_up_to_date(repo_path: Path) -> bool:
    """
    Return True iff the local HEAD matches origin/main and the working tree
    has no dirty files.
    """
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        return False

    if not repo.remotes:
        return False

    try:
        repo.remotes.origin.fetch()
    except Exception:
        return False

    for branch_name in ("main", "master"):
        try:
            remote_branch = repo.remotes.origin.refs[branch_name]
            break
        except IndexError:
            continue
    else:
        return False

    return (
        repo.head.commit.hexsha == remote_branch.commit.hexsha
        and not repo.is_dirty(untracked_files=True)
    )


def build_messages(
    history,
    system_prompt,
    repo_docs,
    user_input=None,
):
    """
    Build the list of messages expected by the OpenAI chat API.
    """
    msgs = [{"role": "system", "content": str(system_prompt)}]
    if repo_docs:
        msgs.append({"role": "assistant", "content": str(repo_docs)})

    for u, a in history:
        msgs.append({"role": "user", "content": str(u)})
        msgs.append({"role": "assistant", "content": str(a)})

    if user_input is not None:
        msgs.append({"role": "user", "content": str(user_input)})

    return msgs


def stream_and_collect(client, messages, tools, placeholder):
    """
    Stream a response from the model, updating `placeholder` live, and
    collect any tool calls that are emitted.
    """
    stream = client.chat.completions.create(
        model="unsloth/gpt-oss-20b-GGUF:F16",
        messages=messages,
        stream=True,
        tools=tools,
    )

    full_resp = ""
    tool_calls_buffer = {}

    for chunk in stream:
        delta = chunk.choices[0].delta

        # Regular text
        if delta.content:
            full_resp += delta.content
            placeholder.markdown(full_resp, unsafe_allow_html=True)

        # Tool calls
        if delta.tool_calls:
            for tc_delta in delta.tool_calls:
                idx = tc_delta.index
                if idx not in tool_calls_buffer:
                    tool_calls_buffer[idx] = {
                        "id": tc_delta.id,
                        "name": tc_delta.function.name,
                        "arguments": "",
                    }
                if tc_delta.function.arguments:
                    tool_calls_buffer[idx]["arguments"] += tc_delta.function.arguments

    final_tool_calls = list(tool_calls_buffer.values()) if tool_calls_buffer else None
    return full_resp, final_tool_calls


# --------------------------------------------------------------------------- #
#  Streamlit UI
# --------------------------------------------------------------------------- #
def main():
    st.set_page_config(page_title="Chat with GPT‑OSS", layout="wide")
    REPO_PATH = Path(__file__).parent

    # Session state
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("system_prompt", DEFAULT_SYSTEM_PROMPT)
    st.session_state.setdefault("repo_docs", "")
    st.session_state.has_pushed = is_repo_up_to_date(REPO_PATH)

    # -------------------------------------------------------------------- #
    #  Sidebar
    # -------------------------------------------------------------------- #
    with st.sidebar:
        st.header("Settings")

        # System prompt editor
        prompt = st.text_area(
            "System prompt",
            st.session_state.system_prompt,
            height=120,
        )
        if prompt != st.session_state.system_prompt:
            st.session_state.system_prompt = prompt

        # New chat button
        if st.button("New Chat"):
            st.session_state.history = []
            st.session_state.repo_docs = ""
            st.success("Chat history cleared. Start fresh!")

        # Refresh docs button
        if st.button("Refresh Docs"):
            st.session_state.repo_docs = refresh_docs()
            st.success("Codebase docs updated!")

        # Push to GitHub button
        if st.button("Push to GitHub"):
            with st.spinner("Pushing to GitHub…"):
                try:
                    from app.push_to_github import main as push_main

                    push_main()
                    st.session_state.has_pushed = True
                    st.success("✅  Repository pushed to GitHub.")
                except Exception as exc:
                    st.error(f"❌  Push failed: {exc}")

        # Push status
        status = "✅  Pushed" if st.session_state.has_pushed else "⚠️  Not pushed"
        st.markdown(f"**Push status:** {status}")

        # Available tools
        st.subheader("Available tools")
        for t in TOOLS:
            st.markdown(f"- **{t.name}**: {t.description}")

    # -------------------------------------------------------------------- #
    #  Chat history
    # -------------------------------------------------------------------- #
    for user_msg, bot_msg in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(user_msg)
        with st.chat_message("assistant"):
            st.markdown(bot_msg)

    # -------------------------------------------------------------------- #
    #  User input
    # -------------------------------------------------------------------- #
    if user_input := st.chat_input("Enter request…"):
        with st.chat_message("user"):
            st.markdown(user_input)

        client = get_client()
        tools = get_tools()
        msgs = build_messages(
            st.session_state.history,
            st.session_state.system_prompt,
            st.session_state.repo_docs,
            user_input,
        )
        with st.chat_message("assistant"): placeholder = st.empty()
        final_text, tool_calls = stream_and_collect(client, msgs, tools, placeholder)

        st.session_state.history.append((user_input, final_text))

        # -----------------------------------------------------------------
        #  Handle a single tool call (the example only expects one)
        # -----------------------------------------------------------------
        if tool_calls:
            tool_call = tool_calls[0]
            try:
                args = json.loads(tool_call.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}

            func = next((t.func for t in TOOLS if t.name == tool_call.get("name")), None)

            if func is None:
                tool_result = f"⚠️  Tool '{tool_call.get("name")}' not registered."
            else:
                try:
                    tool_result = func(**args)
                except Exception as exc:
                    tool_result = f"❌  Tool error: {exc}"

            # Append tool call result to the current placeholder
            tool_output_str = (
                f"**Tool call**: `{tool_call.get('name')}`"
                f"({', '.join(f'{k}={v}' for k, v in args.items())}) → `{tool_result}`"
            )
            # Update the placeholder with the tool output (keeps the streamed text)
            placeholder.markdown(final_text + "\n\n" + tool_output_str, unsafe_allow_html=True)

            # Tell the model the result of the tool call
            assistant_tool_call_msg = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call.get("id"),
                        "type": "function",
                        "function": {
                            "name": tool_call.get("name"),
                            "arguments": tool_call.get("arguments") or "{}",
                        },
                    }
                ],
            }

            tool_msg = {
                "role": "tool",
                "tool_call_id": str(tool_call.get("id") or ""),
                "content": str(tool_result or ""),
            }

            msgs2 = build_messages(
                st.session_state.history,
                st.session_state.system_prompt,
                st.session_state.repo_docs,
            )
            msgs2.append(assistant_tool_call_msg)
            msgs2.append(tool_msg)

            with st.chat_message("assistant") as assistant_msg2:
                placeholder2 = st.empty()
                final_text2, _ = stream_and_collect(client, msgs2, tools, placeholder2)

            st.session_state.history[-1] = (user_input, final_text2)

    # -------------------------------------------------------------------- #
    #  Browser‑leaving guard
    # -------------------------------------------------------------------- #
    has_pushed = st.session_state.get("has_pushed", False)
    components.html(
        f"""
        <script>
        window.top.hasPushed = {str(has_pushed).lower()};
        window.top.onbeforeunload = function (e) {{
            if (!window.top.hasPushed) {{
                e.preventDefault(); e.returnValue = '';
                return 'You have not pushed to GitHub yet.\\nDo you really want to leave?';
            }}
        }};
        </script>
        """,
        height=0,
    )


if __name__ == "__main__":
    main()