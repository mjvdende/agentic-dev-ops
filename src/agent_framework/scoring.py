"""Score an audit report against examples/sample-app/KNOWN_ISSUES.md (ADR 0005).

Keyword heuristic: an issue counts as found when any of its patterns appears in the
report (case-insensitive). Spot-check results manually; record them in docs/TEST_RESULTS.md.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnownIssue:
    id: int
    area: str
    title: str
    severity: str
    patterns: tuple[str, ...]


KNOWN_ISSUES: tuple[KnownIssue, ...] = (
    KnownIssue(1, "Dockerfile", "Unpinned `python:latest` base image", "Medium", (r"python:latest", r"unpinned base")),
    KnownIssue(
        2,
        "Dockerfile",
        "Secret in `ENV API_TOKEN`",
        "High",
        (r"env\W+api_token", r"secret.{0,40}(env|dockerfile)", r"api_token.{0,60}(secret|hardcoded)"),
    ),
    KnownIssue(
        3,
        "Dockerfile",
        "`ADD` instead of `COPY` / no `.dockerignore`",
        "Medium",
        (r"\badd\b.{0,40}\bcopy\b", r"\.dockerignore"),
    ),
    KnownIssue(4, "Dockerfile", "Runs as root", "High", (r"\broot\b", r"non-root", r"\buser\b instruction")),
    KnownIssue(
        5,
        "Dockerfile",
        "apt bloat / cache not cleaned",
        "Low",
        (r"apt", r"no-install-recommends", r"/var/lib/apt/lists"),
    ),
    KnownIssue(
        6,
        "Dockerfile",
        "pip cache / unpinned requirements",
        "Medium",
        (r"no-cache-dir", r"unpinned (python )?dependenc", r"pin.{0,30}(requirements|versions)"),
    ),
    KnownIssue(
        7,
        "Dockerfile",
        "Port 22 / shell-form CMD / dev server / no HEALTHCHECK",
        "Medium",
        (r"port 22", r"expose 22", r"healthcheck", r"gunicorn", r"development server", r"exec.form"),
    ),
    KnownIssue(
        8,
        "app.py",
        "Command injection via `shell=True`",
        "Critical",
        (r"shell\s*=\s*true", r"command injection", r"shell injection.{0,60}(ping|app\.py|subprocess)"),
    ),
    KnownIssue(9, "app.py", "`debug=True`", "Critical", (r"debug\s*=\s*true", r"debug mode")),
    KnownIssue(10, "app.py", "Insecure default token `changeme`", "Medium", (r"changeme", r"default (token|secret)")),
    KnownIssue(
        11,
        "CI",
        "Hardcoded registry password",
        "High",
        (r"supersecret", r"hardcoded (registry )?(credential|password)", r"docker login.{0,40}-p"),
    ),
    KnownIssue(12, "CI", "`latest` image tags", "Medium", (r"docker:latest", r"sample-app:latest")),
    KnownIssue(13, "CI", "`curl | bash`", "High", (r"curl[^|\n]{0,40}\|\s*(ba)?sh", r"remote script")),
    KnownIssue(14, "CI", "No test/scan stage", "Medium", (r"(test|scan)(ning)? stage", r"trivy", r"no tests?\b")),
)


def score(report: str) -> dict[int, bool]:
    text = report.lower()
    return {i.id: any(re.search(p, text) for p in i.patterns) for i in KNOWN_ISSUES}


def summary(found: dict[int, bool]) -> str:
    hits = sum(found.values())
    lines = [f"Found {hits}/{len(KNOWN_ISSUES)} known issues", ""]
    lines += [f"  [{'x' if found[i.id] else ' '}] #{i.id:<2} {i.area:<10} {i.title}" for i in KNOWN_ISSUES]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        sys.exit("usage: score-audit <report.md>")
    print(summary(score(Path(argv[0]).read_text())))


if __name__ == "__main__":
    main()
