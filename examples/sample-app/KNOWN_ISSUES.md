# Known issues (intentional)

This app is a **test target** for the agents (ADR 0005). Every flaw below is deliberate. **Do not fix them in place.** Agent runs are scored by how many of these they find.

All secrets here are fake demo values.

## Dockerfile

| # | Issue | Severity |
|---|---|---|
| 1 | `FROM python:latest`: unpinned, large base image | Medium |
| 2 | `ENV API_TOKEN=...`: secret baked into the image | High |
| 3 | `ADD .` instead of `COPY`; no `.dockerignore` (copies `.git`, CI file, etc.) | Medium |
| 4 | Runs as root (no `USER`) | High |
| 5 | `apt-get install` without `--no-install-recommends`, extra tools (`vim`, `curl`), apt lists not cleaned | Low |
| 6 | `pip install` without `--no-cache-dir`; requirements unpinned (`requirements.txt`) | Medium |
| 7 | `EXPOSE 22`: unneeded port; shell-form `CMD`; Flask dev server used in production; no `HEALTHCHECK` | Medium |

## Application (`app.py`)

| # | Issue | Severity |
|---|---|---|
| 8 | `/ping` passes user input to `subprocess.run(..., shell=True)`: command injection | Critical |
| 9 | `debug=True`: Werkzeug debugger allows remote code execution | Critical |
| 10 | Insecure default `API_TOKEN="changeme"` | Medium |

## CI (`.gitlab-ci.yml`)

| # | Issue | Severity |
|---|---|---|
| 11 | Registry password hardcoded in `docker login -p` | High |
| 12 | `docker:latest` / `:latest` image tags: not reproducible | Medium |
| 13 | `curl ... \| bash`: running an unverified remote script | High |
| 14 | No test or scan stage before deploy | Medium |
