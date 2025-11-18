# Repository Guidelines

## Project Structure & Module Organization
- Core integration lives in `custom_components/ha_backup_octopus/`; `__init__.py` wires the Home Assistant domain, `backup_manager.py` orchestrates handlers, and `handlers/` contains device-specific implementations (base + WLED example).
- Tests sit under `tests/ha_backup_octopus/` and mirror handler names; add new test modules alongside new handlers.
- Architecture notes and future plans live in `docs/design.md`. Use it as the source of truth for extension points and storage layout assumptions.
- Devcontainer config (`.devcontainer/devcontainer.json`) binds `custom_components` into the Home Assistant dev image; use this to hack against a realistic HA environment.

## Build, Test, and Development Commands
- `python -m pytest tests` — run the test suite locally; keep tests fast and hermetic (avoid hitting real devices).
- `python -m pytest tests/ha_backup_octopus/testWLED.py -k WLED` — run a focused handler test during development.
- When developing inside the HA devcontainer, rely on the mounted `custom_components` path; restart Home Assistant after substantial changes to reload the integration.

## Coding Style & Naming Conventions
- Python 3.11+ with 4-space indentation; prefer type hints and async-friendly patterns (async/await, `aiohttp` sessions).
- Handlers subclass `DeviceBackupHandler` and should be named `{Device}BackupHandler` in `handlers/{device}.py`; expose minimal state and keep I/O contained within `fetch_backup`.
- Persist files under the per-device backup folder provided by `run_backup`; avoid hardcoded absolute paths.
- Keep logging/output concise; prefer Home Assistant logging over `print` once integrated.

## Testing Guidelines
- Use `pytest` for all tests; name tests `test<Handler>.py` and coroutines `test_<behavior>`.
- Mock network calls for handlers (e.g., `aiohttp.ClientSession`) rather than hitting real devices; keep fixtures small and deterministic.
- Add regression tests when changing backup folder logic or handler protocols.

## Commit & Pull Request Guidelines
- Commit messages: short, imperative subject lines (e.g., “Add FritzBox handler”, “Refine backup folder selection”); include scope when helpful.
- Pull requests should describe behavior changes, risks, and testing performed; link to issues when available.
- Include screenshots/log snippets only when debugging UI-related or HA log changes; otherwise keep PRs text-first and focused on code + tests.
