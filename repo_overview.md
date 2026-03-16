| Relative path | Function | Description |
|---------------|----------|-------------|
| nbchat/core/client.py | get_client |  |
| nbchat/core/compressor.py | _get_session |  |
| nbchat/core/compressor.py | init_session | Initialise (or reset) compression state for *session_id*. |
| nbchat/core/compressor.py | clear_session | Remove all compression state for *session_id* (call on session reset). |
| nbchat/core/compressor.py | get_compression_stats | Return a snapshot of per-tool compression statistics.  Returns a dict mapping ``tool_name`` → ``{calls, compressed_calls, compression_rate, avg_ratio, strategies}``.  ``avg_ratio < 1.0`` means output was on average compressed. ``compression_rate`` is the fraction of calls that triggered compression. |
| nbchat/core/compressor.py | reset_compression_stats | Clear all accumulated compression statistics (useful in tests). |
| nbchat/core/compressor.py | _record_stat |  |
| nbchat/core/compressor.py | _extract_key_arg | Extract the primary string argument (usually a file path) from JSON tool args.  Used as the identity key for repeat-read detection. |
| nbchat/core/compressor.py | _detect_file_extension | Detect file extension from JSON tool arguments.  Returns the extension (e.g. '.py') in lower case, or '' if undetectable. |
| nbchat/core/compressor.py | _python_skeleton | Extract an importable skeleton from Python source using the AST.  Preserves: imports, top-level assignments, function/async-function signatures (with short docstrings), class definitions with all method signatures (with short docstrings).  Function bodies are replaced with '...'.  Returns None on SyntaxError so the caller can fall back to head+tail. |
| nbchat/core/compressor.py | _json_skeleton | Summarise JSON structure: key names, value types, and counts. |
| nbchat/core/compressor.py | _yaml_skeleton | Extract top-level YAML keys without requiring PyYAML. |
| nbchat/core/compressor.py | _js_skeleton | Extract function/class/export signatures from JS/TS using regex. |
| nbchat/core/compressor.py | _syntax_aware_truncate | Dispatch to the appropriate skeleton extractor.  Returns None when no extractor applies or extraction fails — the caller should fall back to head+tail in that case. |
| nbchat/core/compressor.py | _head_tail | Symmetric head+tail truncation preserving both ends of the output. |
| nbchat/core/compressor.py | compress_tool_output | Return a compressed version of *result* bounded to MAX_TOOL_OUTPUT_CHARS.  Strategy (evaluated in priority order):  1. Short output (≤ MAX_TOOL_OUTPUT_CHARS) — pass through unchanged. 2. Session lossless set — tool was learned to be lossy; use head+tail,    skip LLM/skeleton. 3. Repeat-read detection — if this exact (tool_name, key_arg) was    compressed recently, the model is re-requesting it because the    compression lost information.  Add to session lossless set and return    head+tail immediately. 4. File-read tool + structured extension — apply syntax-aware skeleton    extraction (AST for Python, structural for JSON/YAML/JS). 5. File-read / command tool — head+tail truncation; no LLM, no relevance    filtering (filtering causes re-read loops). 6. All other tools — LLM structural compression.  Side effects:   • Compression statistics are updated for every call.   • Session lossless set may be updated on repeat-read detection.  Parameters ---------- session_id:     Pass the current session ID to enable per-session lossless learning     and repeat-read detection.  Pass "" (default) to disable both. |
| nbchat/core/config.py | _load_yaml |  |
| nbchat/core/db.py | _is_error_content | Check if content contains error indicators. |
| nbchat/core/db.py | init_db | Create tables if they do not exist. Idempotent. |
| nbchat/core/db.py | log_message |  |
| nbchat/core/db.py | log_row |  |
| nbchat/core/db.py | log_tool_msg |  |
| nbchat/core/db.py | load_history |  |
| nbchat/core/db.py | get_session_ids |  |
| nbchat/core/db.py | replace_session_history |  |
| nbchat/core/db.py | _meta_set |  |
| nbchat/core/db.py | _meta_get |  |
| nbchat/core/db.py | save_context_summary |  |
| nbchat/core/db.py | load_context_summary |  |
| nbchat/core/db.py | save_turn_summaries | Persist the full in-memory turn-summary cache for *session_id*. |
| nbchat/core/db.py | load_turn_summaries | Return the stored turn-summary cache, or {} if none exists. |
| nbchat/core/db.py | save_task_log |  |
| nbchat/core/db.py | load_task_log |  |
| nbchat/core/db.py | append_episodic | Append one tool-exchange record to the episodic store. |
| nbchat/core/db.py | query_episodic_by_entities | Return episodic entries whose entity_refs overlap with *entity_refs*.  Uses a LIKE search over the JSON-encoded entity_refs column so no JSON extension is required.  Returns rows sorted by importance_score DESC. |
| nbchat/core/db.py | query_episodic_top_importance | Return the highest-importance episodic entries for *session_id*. |
| nbchat/core/db.py | delete_episodic_for_session | Remove all episodic entries for *session_id* (used on session reset). |
| nbchat/core/db.py | get_core_memory | Return all core memory slots for *session_id* as a plain dict. |
| nbchat/core/db.py | set_core_memory_key | Upsert a single core memory slot. |
| nbchat/core/db.py | update_core_memory | Upsert multiple core memory slots in a single transaction. |
| nbchat/core/db.py | clear_core_memory | Delete all core memory entries for *session_id* (used on session reset). |
| nbchat/core/db.py | save_global_monitoring_stats | Persist cross-session monitoring aggregates to session_meta.  Uses the sentinel session_id '__global__' so no new table is required. The value is JSON-serialised and stored under key 'monitoring_global_v1'. |
| nbchat/core/db.py | load_global_monitoring_stats | Load cross-session monitoring aggregates from session_meta.  Returns the parsed dict, or None if no data has been saved yet. |
| nbchat/core/monitoring.py | parse_last_completion_metrics | Parse the most recent completed LLM call from the llama.cpp server log.  Reads the last _LOG_TAIL_BYTES from the file and extracts cache metrics for the final completion block.  Returns an invalid _CacheMetrics if the log is absent or the block cannot be parsed. |
| nbchat/core/monitoring.py | _detect_warnings |  |
| nbchat/core/monitoring.py | _empty_global |  |
| nbchat/core/monitoring.py | merge_into_global | Return a new global stats dict with session_data merged in.  Both dicts follow the shape returned by SessionMonitor.to_mergeable(). Pure function — does not mutate either argument. |
| nbchat/core/monitoring.py | get_global_report | Compute derived metrics from raw global stats.  Returns a report dict with the same structure as SessionMonitor.get_session_report() but aggregated across all sessions. |
| nbchat/core/monitoring.py | suggest_config | Return a list of concrete config change suggestions.  Each suggestion is a dict: {     "priority": "high" | "medium" | "low",     "target": "<config key or tool name>",     "action": "<what to change>",     "reason": "<evidence summary>", } |
| nbchat/core/monitoring.py | get_session_monitor | Return the SessionMonitor for *session_id*, creating it if needed. |
| nbchat/core/monitoring.py | flush_session_monitor | Merge session monitor data into global stats and persist.  Call this at the end of a session or when switching sessions.  Parameters ---------- db: the nbchat.core.db module (passed to avoid circular imports) |
| nbchat/core/monitoring.py | format_report | Return a human-readable summary of a session or global report. |
| nbchat/core/monitoring.py | format_monitoring_html | Render monitoring data as compact HTML for the sidebar widget.  Parameters ---------- session_report:     Output of SessionMonitor.get_session_report(). global_report:     Output of get_global_report(), or None if no cross-session data yet. code_color:     Hex color for code/metric values — should match CODE_COLOR in styles.py.  Layout ------ - Session cache metrics (open by default) - Per-tool rows inside a nested collapsible - Warnings always visible (not collapsed) — prominent orange text - Global stats + suggestions (collapsed by default) |
| nbchat/core/remote.py | _token | Return the GitHub PAT from the environment. |
| nbchat/core/remote.py | _remote_url | Return an HTTPS URL that contains the PAT.  Parameters ---------- repo_name:     The repository name to use in the URL.  If ``None`` the default     :data:`~nbchat.core.config.REPO_NAME` is used. |
| nbchat/core/retry.py | _is_retryable | Check if an error is retryable based on error message. |
| nbchat/core/retry.py | _calculate_delay | Calculate delay with exponential backoff and jitter. |
| nbchat/core/retry.py | retry | Decorator to add retry logic to a function.  Args:     func: Function to decorate     max_retries: Maximum number of retry attempts     initial_delay: Initial delay in seconds     max_delay: Maximum delay in seconds     backoff_multiplier: Multiplier for exponential backoff     on_retry: Optional callback when retry occurs (attempt, error, next_delay)  Returns:     Decorated function with retry logic |
| nbchat/core/retry.py | retry_with_backoff | Execute a function with retry logic and exponential backoff.  Args:     func: Function to execute     args: Positional arguments for func     max_retries: Maximum number of retry attempts     initial_delay: Initial delay in seconds     max_delay: Maximum delay in seconds     backoff_multiplier: Multiplier for exponential backoff     on_retry: Optional callback when retry occurs     kwargs: Keyword arguments for func  Returns:     Result of func  Raises:     Exception: If all retries fail |
| nbchat/core/utils.py | lazy_import | Import a module only when needed.  The function mirrors the behaviour of the legacy ``lazy_import``. |
| nbchat/tools/__init__.py | _generate_schema |  |
| nbchat/tools/__init__.py | get_tools | Return the list of tools formatted for chat.completions.create. |
| nbchat/tools/browser.py | _hint |  |
| nbchat/tools/browser.py | _err | Return a JSON error envelope.  Callers may supply a custom hint; otherwise one is derived from the message text via _hint(). Extra keyword arguments are merged into the response dict. |
| nbchat/tools/browser.py | browser | Stateless browser tool. Launches a fresh Chromium instance per call.  Parameters ---------- url:     The page to visit. Must include scheme (https://...). A missing scheme     is auto-corrected to https://. actions:     Optional list of interactions performed *before* content extraction.     Supported types:      - ``{"type": "click",      "selector": "CSS"}``     - ``{"type": "type",       "selector": "CSS", "text": "value"}``       Empty string is valid (clears the field). Key must be present.     - ``{"type": "select",     "selector": "CSS", "value": "option"}``     - ``{"type": "wait",       "selector": "CSS"}``     - ``{"type": "wait",       "timeout": 2000}``     - ``{"type": "scroll",     "direction": "down"|"up", "amount": 500}``       ``amount`` is always treated as positive; ``direction`` controls sign.     - ``{"type": "navigate",   "url": "https://..."}``       HTTP errors and timeouts on navigate are treated as action errors.     - ``{"type": "screenshot", "path": "file.png"}``      Action errors are non-fatal: logged in ``action_errors``, ``status``     set to ``"partial"``, and execution continues with the next action. selector:     CSS selector to scope text extraction to one element. When set, ``title``     is omitted from the response. Omit for full-page extraction. extract_elements:     When True, include ``interactive`` (buttons, inputs, links) and ``links``     in the response — useful for discovering what actions are available. navigation_timeout:     Milliseconds to wait for page navigation (default 30 000). action_timeout:     Milliseconds to wait for each action's selector/interaction (default 5 000). max_content_length:     Maximum characters of page text returned (default 8 000). wait_until:     Playwright navigation event — one of ``"commit"``, ``"domcontentloaded"``     (default, fastest), ``"load"``, or ``"networkidle"`` (slowest).  Returns ------- str     Always valid JSON. On success::          {             "status": "success" | "partial",             "url": "https://...",             "title": "...",          # omitted when selector= is set             "content": "...",             "actions": [...],        # omitted when no actions were given             "action_errors": [...],  # omitted when all actions succeeded             "interactive": [...],    # included when extract_elements=True             "links": [...]           # included when extract_elements=True         }      On failure::          {"error": "...", "hint": "..."} |
| nbchat/tools/create_file.py | _safe_resolve | Resolve ``rel_path`` against ``repo_root`` and ensure the result does **not** escape the repository root (prevents directory traversal). |
| nbchat/tools/create_file.py | _create_file | Create a new file at ``path`` (relative to the repository root) with the supplied ``content``.  Parameters ---------- path     File path relative to the repo root.  ``path`` may contain     directory separators but **must not** escape the root. content     Raw text to write into the file.  Returns ------- str     JSON string.  On success:      .. code-block:: json          { "result": "File created: <path>" }      On failure:      .. code-block:: json          { "error": "<exception message>" } |
| nbchat/tools/get_weather.py | _geocode_city | Return latitude and longitude for a given city name.  The function queries the OpenMeteo geocoding API and returns the first result.  It raises a :class:`ValueError` if the city cannot be found. |
| nbchat/tools/get_weather.py | _fetch_weather | Fetch current and daily forecast weather data for the given coordinates and date.  Parameters ---------- lat, lon: float     Latitude and longitude of the location. date: str     ISO 8601 formatted date string (YYYY-MM-DD).  The API expects a     single day, so ``start_date`` and ``end_date`` are identical. |
| nbchat/tools/get_weather.py | _get_weather | Retrieve current and forecast weather information for a given city and date.  Parameters ---------- city: str     The name of the city to look up. date: str, optional     The date for which to retrieve forecast data (ISO format YYYY-MM-DD).     If omitted or empty, today's date is used. |
| nbchat/tools/make_change_to_file.py | _safe_resolve | Resolve ``rel_path`` against ``repo_root`` and guard against directory traversal. Normalize to NFKC to ensure characters like '..' or '/' aren't spoofed |
| nbchat/tools/make_change_to_file.py | _extract_payload |  |
| nbchat/tools/make_change_to_file.py | apply_diff |  |
| nbchat/tools/make_change_to_file.py | _trim_overlap | Trims the end of ins_lines if they already exist at the start of following_lines. Prevents duplicate 'stitching' when the diff and file overlap. |
| nbchat/tools/make_change_to_file.py | _normalize_diff_lines | Clean the diff and strip Unified Diff metadata headers. |
| nbchat/tools/make_change_to_file.py | _detect_newline |  |
| nbchat/tools/make_change_to_file.py | _is_done |  |
| nbchat/tools/make_change_to_file.py | _read_str |  |
| nbchat/tools/make_change_to_file.py | _parse_create_diff |  |
| nbchat/tools/make_change_to_file.py | _parse_update_diff |  |
| nbchat/tools/make_change_to_file.py | _advance_cursor |  |
| nbchat/tools/make_change_to_file.py | _read_section |  |
| nbchat/tools/make_change_to_file.py | _equals_slice | Helper to compare a slice of lines using a transformation function (like strip). |
| nbchat/tools/make_change_to_file.py | _find_context |  |
| nbchat/tools/make_change_to_file.py | _apply_chunks |  |
| nbchat/tools/make_change_to_file.py | make_change_to_file | Apply a unified diff to a file inside the repository.  Parameters ---------- path : str     Relative file path (under the repo root). op_type : str     One of ``create``, ``update`` or ``delete``. diff : str     Unified diff string (ignored for ``delete``).  Returns ------- str     JSON string with either ``result`` or ``error``. |
| nbchat/tools/push_to_github.py | push_to_github | Push the current repository to GitHub.  Parameters ---------- commit_message:     Commit message for the auto commit.  Defaults to ``"Auto commit"``. rebase:     Whether to rebase during pull.  Defaults to ``False`` to mirror     the original behaviour. |
| nbchat/tools/repo_overview.py | walk_python_files | Return a sorted list of all ``.py`` files under *root*. |
| nbchat/tools/repo_overview.py | extract_functions_from_file | Return a list of (function_name, docstring) for top‑level functions.  Functions defined inside classes or other functions are ignored. |
| nbchat/tools/repo_overview.py | build_markdown_table |  |
| nbchat/tools/repo_overview.py | func | Generate a markdown table of all top‑level Python functions.  The table is written to ``repo_overview.md`` in the repository root. |
| nbchat/tools/run_command.py | _safe_resolve | Resolve ``rel_path`` against ``repo_root`` and ensure the result does **not** escape the repository root (prevents directory traversal). |
| nbchat/tools/run_command.py | _run_command | Execute ``command`` in the repository root and return a JSON string with:     * ``stdout``     * ``stderr``     * ``exit_code`` Any exception is converted to an error JSON.  The ``cwd`` argument is accepted for backward compatibility but ignored; the command is always executed in the repository root. |
| nbchat/tools/run_tests.py | _run_tests | Execute `pytest -q` in the repository root and return JSON. |
| nbchat/tools/send_email.py | _send_email | Send an email via Gmail.  Parameters ---------- subject: str     Subject line of the email. body: str     Plain‑text body of the email.  Returns ------- str     JSON string containing either ``result`` or ``error``. |
| nbchat/tools/test_browser.py | ok |  |
| nbchat/tools/test_browser.py | err |  |
| nbchat/tools/test_browser.py | _make_playwright_mock |  |
| nbchat/tools/test_browser.py | _patch |  |
| nbchat/tools/test_browser.py | _run | Convenience: run browser() with a mock and return (data, page). |
| nbchat/ui/chat_builder.py | build_messages | Build OpenAI messages from internal chat history.  Parameters ---------- history:     List of canonical 6-tuples:     ``(role, content, tool_id, tool_name, tool_args, error_flag)``.     Should already be pre-windowed (via _window()) to the last N user     turns.  Leading ``("system", …)`` rows (L1/L2/prior context blocks     injected by ContextMixin._window()) are extracted and placed into     the volatile context turn rather than messages[0]. system_prompt:     The static system message.  Written verbatim to ``messages[0]``     and never modified — this is the contract that enables KV caching. task_log:     Optional list of recent action strings maintained by ChatUI.     Included in the volatile context turn (messages[1]) so the model     always knows what it has been doing even when old messages are     outside the window.  Message layout -------------- messages[0]  {"role": "system",    "content": system_prompt}  <- static messages[1]  {"role": "user",      "content": "[SESSION CONTEXT]..."}  <- volatile messages[2]  {"role": "assistant", "content": "Context received."}     <- volatile messages[3+] actual conversation turns (user / assistant / tool)  messages[1] and messages[2] are omitted when there is no volatile content (empty task_log and no leading system rows in history), keeping the message list minimal for fresh sessions.  Notes ----- Many local-model servers (llama.cpp, Ollama, ...) enforce via their Jinja chat template that the *system* role may only appear as the very first message.  This function never emits more than one system-role message. Any ``("system", …)`` rows that appear *after* conversation content (which should not occur in normal operation but may surface in legacy DB rows) are demoted to user-role ``[CONTEXT NOTE]`` messages.  ``("analysis", …)`` rows are reasoning traces — display-only, never sent to the model. |
| nbchat/ui/chat_renderer.py | render_user |  |
| nbchat/ui/chat_renderer.py | render_assistant |  |
| nbchat/ui/chat_renderer.py | render_reasoning |  |
| nbchat/ui/chat_renderer.py | render_tool |  |
| nbchat/ui/chat_renderer.py | render_assistant_with_tools |  |
| nbchat/ui/chat_renderer.py | render_assistant_full |  |
| nbchat/ui/chat_renderer.py | render_system |  |
| nbchat/ui/chat_renderer.py | render_placeholder |  |
| nbchat/ui/chat_renderer.py | render_compacted_summary |  |
| nbchat/ui/context_manager.py | _parse_structured_summary | Parse a GOAL/ENTITIES/RATIONALE structured summary into a dict. |
| nbchat/ui/context_manager.py | _extract_entities | Extract entity references (file paths, API paths, URLs) from *text*.  Returns a deduplicated list capped at 10 entries. |
| nbchat/ui/context_manager.py | _group_by_user_turn | Split *rows* into per-user-turn groups. |
| nbchat/ui/conversation.py | _is_error_content | Return True if *content* contains common error signal keywords. |
| nbchat/ui/conversation.py | _sanitize_messages | Normalize assistant messages for strict OpenAI-compat models.  The OpenAI spec requires content=None (not "") when tool_calls are present on an assistant message.  Smaller models fail to emit structured tool calls on subsequent turns when they see content="" alongside tool_calls in their history.  This sanitizer fixes both freshly built messages and old DB rows reconstructed via assistant_full. |
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
| nbchat/ui/styles.py | make_widget | Return an :class:`ipywidgets.HTML` widget.  The original code defined this function inside ``compacted_summary_html`` due to a stray indentation.  That made the module fail to import.  The function is now defined at module level. |
| nbchat/ui/tool_executor.py | run_tool | Execute a tool with arguments and return the (trimmed) string result.  Includes retry policy inspired by openclaw (https://docs.openclaw.ai/concepts/retry). |
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
| tests/test_chat_builder.py | _row | Convenience factory for canonical 6-tuples. |
| tests/test_compressor.py | _mock_client |  |
| tests/test_compressor.py | _short |  |
| tests/test_compressor.py | _long |  |
| tests/test_context_manager.py | _row |  |
| tests/test_context_manager.py | _make_config |  |
| tests/test_context_manager.py | _patched_window |  |
| tests/test_monitoring.py | _make_log | Write a fake llama.cpp log containing one completion block. |