# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: Flask entrypoint; routes, responses, and config.
- `music_api.py`: NetEase API wrapper (song URL/detail, lyric, playlist/album, QR login).
- `music_downloader.py`: File downloads, async batch helpers, and tag writing (MP3/FLAC/M4A).
- `enhanced_download.py`: Batch download (v2) with background thread + SSE progress.
- `download_progress.py`: In‑memory task tracking for batch jobs.
- `cookie_manager.py`: Read/validate/backup cookies from `cookie.txt`.
- `templates/index.html`: Single‑page UI (Bootstrap 5, Bootstrap Icons, jQuery, APlayer).
- `downloads/`: Output directory for saved audio files.

## Build, Test, and Development Commands
- Setup (recommended, using uv):
  - `uv venv && uv sync` (creates venv from `pyproject.toml`/`uv.lock`)
  - `source .venv/bin/activate` (Windows: `.\.venv\Scripts\activate`)
- Run locally:
  - `python main.py` (serves on `http://0.0.0.0:5000` by default)
  - Toggle debug by editing `APIConfig.debug = True` in `main.py`.
- Logs:
  - `tail -f music_api.log` for server output.

## Coding Style & Naming Conventions
- Python 3.10+, PEP 8, 4‑space indentation, type hints where practical.
- Names: modules `snake_case.py`, functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Server responses via `APIResponse.success/error` for consistent JSON shape.
- Frontend: keep UI changes in `templates/index.html`; prefer Bootstrap 5 utilities; keep interactions minimal and accessible.

## Testing Guidelines
- Framework: `pytest` (not bundled). Add tests under `tests/` as `tests/test_*.py`.
- Prefer network‑free tests by mocking HTTP (e.g., `requests` responses) and filesystem.
- Aim for coverage of route parameter validation and downloader logic (filename sanitize, tag writing).
- Run: `pytest -q` (after `pip install pytest`).

## Commit & Pull Request Guidelines
- Commits: small, scoped, imperative subject (e.g., "fix: sanitize filenames on Windows").
- PRs: include description, rationale, affected endpoints/files, and screenshots for UI changes.
- Keep backward compatibility for legacy routes (`/Song_V1`, `/Search`, etc.).

## Security & Configuration Tips
- Do not commit real credentials or cookies. Treat `cookie.txt` as sensitive.
- Large tasks should run out‑of‑request (use batch v2 + SSE); avoid long blocking work in routes.
- Review CORS and file size limits in `APIConfig` before deployment.
