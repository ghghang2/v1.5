| Relative path | Function | Description |
|---------------|----------|-------------|
| git_util/push_to_github.py | main | Create/attach the remote, pull, commit and push.  The script accepts an optional ``--repo`` argument or the ``NEW_REPO`` environment variable.  If neither is supplied the default :data:`~nbchat.core.config.REPO_NAME` is used. |
| git_util/remote.py | _token | Return the GitHub PAT from the environment. |
| git_util/remote.py | _remote_url | Return an HTTPS URL that contains the PAT.  Parameters ---------- repo_name:     The repository name to use in the URL.  If ``None`` the default     :data:`~nbchat.core.config.REPO_NAME` is used. |
| nbchat/core/client.py | get_client | Return a client that talks to the local OpenAI‑compatible server. |
| nbchat/core/db.py | init_db | Create the database file and the chat_log table if they do not exist.  The function is idempotent — calling it repeatedly has no adverse effect.  It should be invoked once during application startup. |
| nbchat/core/db.py | log_message | Persist a single chat line.  Parameters ---------- session_id     Identifier of the chat session — e.g. a user ID or a UUID. role     Role of the speaker (e.g., "user", "assistant"). content     The raw text sent or received. |
| nbchat/core/db.py | log_tool_msg | Persist a single tool message.  Parameters ---------- session_id     Identifier of the chat session. tool_id     Identifier for the tool call. tool_name     Human‑readable tool name. tool_args     JSON string of the arguments passed to the tool. content     Result of the tool execution. |
| nbchat/core/db.py | load_history | Return the last *limit* chat pairs for the given session.  The returned list contains tuples of ``(role, content, tool_id, tool_name, tool_args)`` in the order they were inserted.  ``limit`` is applied to the number of rows returned. |
| nbchat/core/db.py | get_session_ids | Return a list of all distinct session identifiers stored in the DB. |
| nbchat/core/db.py | replace_session_history | Replace all rows for a session with the compacted history. |
| nbchat/core/utils.py | lazy_import | Import a module only when needed.  The function mirrors the behaviour of the legacy ``lazy_import``. |
| nbchat/tools/__init__.py | _generate_schema |  |
| nbchat/tools/__init__.py | get_tools | Return the list of tools formatted for chat.completions.create. |
| nbchat/tools/apply_patch.py | _safe_resolve | Resolve ``rel_path`` against ``repo_root`` and guard against directory traversal. Normalize to NFKC to ensure characters like '..' or '/' aren't spoofed |
| nbchat/tools/apply_patch.py | _extract_payload |  |
| nbchat/tools/apply_patch.py | apply_diff |  |
| nbchat/tools/apply_patch.py | _trim_overlap | Trims the end of ins_lines if they already exist at the start of following_lines. Prevents duplicate 'stitching' when the diff and file overlap. |
| nbchat/tools/apply_patch.py | _normalize_diff_lines | Clean the diff and strip Unified Diff metadata headers. |
| nbchat/tools/apply_patch.py | _detect_newline |  |
| nbchat/tools/apply_patch.py | _is_done |  |
| nbchat/tools/apply_patch.py | _read_str |  |
| nbchat/tools/apply_patch.py | _parse_create_diff |  |
| nbchat/tools/apply_patch.py | _parse_update_diff |  |
| nbchat/tools/apply_patch.py | _advance_cursor |  |
| nbchat/tools/apply_patch.py | _read_section |  |
| nbchat/tools/apply_patch.py | _equals_slice | Helper to compare a slice of lines using a transformation function (like strip). |
| nbchat/tools/apply_patch.py | _find_context |  |
| nbchat/tools/apply_patch.py | _apply_chunks |  |
| nbchat/tools/apply_patch.py | apply_patch | Apply a unified diff to a file inside the repository.  Parameters ---------- path : str     Relative file path (under the repo root). op_type : str     One of ``create``, ``update`` or ``delete``. diff : str     Unified diff string (ignored for ``delete``).  Returns ------- str     JSON string with either ``result`` or ``error``. |
| nbchat/tools/browser.py | browser | Visit a webpage, perform optional interactions, and extract content.  This tool is STATELESS: It opens a browser, runs your commands, and closes. You cannot "keep" the browser open between calls.  Parameters ---------- url : str     The URL to visit. actions : List[Dict], optional     A list of interactions to perform before extracting data.     Supported action types:     - {"type": "click", "selector": "..."}     - {"type": "type", "selector": "...", "text": "..."}     - {"type": "wait", "selector": "..."} (or "timeout": ms)     - {"type": "screenshot", "path": "..."} selector : str, optional     A specific CSS selector to extract text from. If None, returns the full page text. **kwargs :     Handles "hallucinated" nested JSON arguments from some LLMs.  Returns ------- str     JSON string containing the extracted text, source, or operation results. |
| nbchat/tools/create_file.py | _safe_resolve | Resolve ``rel_path`` against ``repo_root`` and ensure the result does **not** escape the repository root (prevents directory traversal). |
| nbchat/tools/create_file.py | _create_file | Create a new file at ``path`` (relative to the repository root) with the supplied ``content``.  Parameters ---------- path     File path relative to the repo root.  ``path`` may contain     directory separators but **must not** escape the root. content     Raw text to write into the file.  Returns ------- str     JSON string.  On success:      .. code-block:: json          { "result": "File created: <path>" }      On failure:      .. code-block:: json          { "error": "<exception message>" } |
| nbchat/tools/get_weather.py | _geocode_city | Return latitude and longitude for a given city name.  The function queries the OpenMeteo geocoding API and returns the first result.  It raises a :class:`ValueError` if the city cannot be found. |
| nbchat/tools/get_weather.py | _fetch_weather | Fetch current and daily forecast weather data for the given coordinates and date.  Parameters ---------- lat, lon: float     Latitude and longitude of the location. date: str     ISO 8601 formatted date string (YYYY-MM-DD).  The API expects a     single day, so ``start_date`` and ``end_date`` are identical. |
| nbchat/tools/get_weather.py | _get_weather | Retrieve current and forecast weather information for a given city and date.  Parameters ---------- city: str     The name of the city to look up. date: str, optional     The date for which to retrieve forecast data (ISO format YYYY-MM-DD).     If omitted or empty, today's date is used. |
| nbchat/tools/repo_overview.py | walk_python_files | Return a sorted list of all ``.py`` files under *root*. |
| nbchat/tools/repo_overview.py | extract_functions_from_file | Return a list of (function_name, docstring) for top‑level functions.  Functions defined inside classes or other functions are ignored. |
| nbchat/tools/repo_overview.py | build_markdown_table |  |
| nbchat/tools/repo_overview.py | func | Generate a markdown table of all top‑level Python functions.  The table is written to ``repo_overview.md`` in the repository root. |
| nbchat/tools/run_command.py | _safe_resolve | Resolve ``rel_path`` against ``repo_root`` and ensure the result does **not** escape the repository root (prevents directory traversal). |
| nbchat/tools/run_command.py | _run_command | Execute ``command`` in the repository root and return a JSON string with:     * ``stdout``     * ``stderr``     * ``exit_code`` Any exception is converted to an error JSON.  The ``cwd`` argument is accepted for backward compatibility but ignored; the command is always executed in the repository root. |
| nbchat/tools/run_tests.py | _run_tests | Execute `pytest -q` in the repository root and return JSON. |
| nbchat/tools/send_email.py | _send_email | Send an email via Gmail.  Parameters ---------- subject: str     Subject line of the email. body: str     Plain‑text body of the email.  Returns ------- str     JSON string containing either ``result`` or ``error``. |
| nbchat/ui/chat_builder.py | build_messages | Build OpenAI messages from internal chat history.  Parameters ---------- history:     List of tuples ``(role, content, tool_id, tool_name, tool_args)``. system_prompt:     The system message to prepend. |
| nbchat/ui/chat_renderer.py | render_user |  |
| nbchat/ui/chat_renderer.py | render_assistant |  |
| nbchat/ui/chat_renderer.py | render_reasoning |  |
| nbchat/ui/chat_renderer.py | render_tool |  |
| nbchat/ui/chat_renderer.py | render_assistant_with_tools |  |
| nbchat/ui/chat_renderer.py | render_assistant_full |  |
| nbchat/ui/chat_renderer.py | render_system |  |
| nbchat/ui/chat_renderer.py | render_placeholder |  |
| nbchat/ui/chat_renderer.py | render_compacted_summary |  |
| nbchat/ui/styles.py | _style |  |
| nbchat/ui/styles.py | _div |  |
| nbchat/ui/styles.py | _style_code | Inject color style into un-styled <code>, <span>, and codehilite <div> tags. |
| nbchat/ui/styles.py | _md |  |
| nbchat/ui/styles.py | _tool_calls_html |  |
| nbchat/ui/styles.py | user_message_html |  |
| nbchat/ui/styles.py | assistant_message_html |  |
| nbchat/ui/styles.py | reasoning_html |  |
| nbchat/ui/styles.py | assistant_full_html |  |
| nbchat/ui/styles.py | assistant_message_with_tools_html |  |
| nbchat/ui/styles.py | tool_result_html |  |
| nbchat/ui/styles.py | system_message_html |  |
| nbchat/ui/styles.py | compacted_summary_html |  |
| nbchat/ui/styles.py | make_widget |  |
| nbchat/ui/tool_executor.py | run_tool | Execute a tool with arguments and return the string result.  Parameters ---------- tool_name:     Name of the tool to execute. args_json:     JSON string containing the arguments for the tool. timeout:     Optional timeout in seconds.  If ``None`` a default of 60 seconds     is used for ``browser`` and ``run_tests`` tools, otherwise 30. |
| nbchat/ui/utils.py | md_to_html | Convert markdown to HTML using fenced code blocks.  This is the same implementation that lived in the legacy file. |
| nbchat/ui/utils.py | changed_files |  |
| run.py | _run | Run a shell command, optionally merging extra environment variables. |
| run.py | _is_port_free |  |
| run.py | _wait_for |  |
| run.py | _save_service_info |  |
| run.py | _load_service_info |  |
| run.py | _kill_pid | Gracefully terminate a process and its children. |
| run.py | main |  |
| run.py | status |  |
| run.py | stop |  |