# Repository Guidelines

## Project Structure & Module Organization

ARL is a Python 3.6 Flask/Celery service backed by MongoDB and RabbitMQ. Application code lives in `app/`: routes are in `app/routes/`, business logic in `app/services/`, helpers in `app/helpers/`, models in `app/modules/`, and utilities in `app/utils/`. Runtime dictionaries and tools are under `app/dicts/` and `app/tools/`. Integrations live in `tools/`; standalone utilities are in `arl_tool/`. Tests are in `test/`, deployment files in `docker/` and `misc/`, and UI assets in `image/`.

## Build, Test, and Development Commands

- `python3.6 -m venv .venv && . .venv/bin/activate`: create and activate a virtual environment.
- `pip install -r requirements.txt`: install pinned dependencies.
- `cp app/config.yaml.example app/config.yaml`: create local configuration.
- `python -m unittest discover -s test -p 'test_*.py'`: run the full unit test suite.
- `python -m compileall app test`: catch syntax errors before submitting changes.
- `python -m app.main`: start the Flask development server on port 5018.
- `gunicorn -b 0.0.0.0:5013 app.main:arl_app -w 4`: run the production-style web process.

Most integrations require MongoDB and RabbitMQ; use `docker/docker-compose.yml` or `misc/*.service`.

## Coding Style & Naming Conventions

Use four-space indentation, explicit imports, and PEP 8-compatible Python. Use `snake_case` for new functions and variables, but preserve neighboring legacy module names. No formatter or linter is configured; keep diffs focused and follow surrounding code. Preserve existing JSON and YAML schemas.

## Testing Guidelines

Tests use standard-library `unittest`. Name files `test/test_<feature>.py`, classes `Test<Feature>`, and methods `test_<behavior>`. Prefer deterministic unit tests and isolate dependencies on networks, databases, queues, external APIs, or bundled scanners. Document unavailable services or expected external failures.

## Commit & Pull Request Guidelines

The visible history establishes no broad convention beyond a date-stamped snapshot commit (`20260802`). Use concise, imperative commit subjects; reserve `YYYYMMDD` subjects for scheduled tool-data updates. Pull requests should describe scope and operational impact, link relevant issues, list test commands and results, and include screenshots for UI changes. Highlight configuration, service, migration, concurrency, or bundled-tool changes.

## Security & Configuration Tips

Never commit `app/config.yaml`, API keys, tokens, passwords, generated certificates, or local logs and databases. Use `app/config.yaml.example` as the template and inspect `git diff` before committing. Run reconnaissance only against authorized targets, and document changes to scanning behavior or external-tool execution.
