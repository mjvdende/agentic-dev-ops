"""Read a project's files into one prompt-ready string (agents have no tools, ADR 0003)."""

from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".idea", ".vscode", "dist", "build", "output"}
# KNOWN_ISSUES.md is the sample app's answer key (ADR 0005).
SKIP_FILES = {"KNOWN_ISSUES.md", ".env", "poetry.lock", "package-lock.json", "yarn.lock"}
MAX_FILE_BYTES = 20_000
MAX_TOTAL_BYTES = 60_000


def iter_project_files(root: Path):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if not path.is_file() or any(part in SKIP_DIRS for part in rel.parts) or path.name in SKIP_FILES:
            continue
        yield path


def read_project(root: Path, max_total: int = MAX_TOTAL_BYTES) -> str:
    """Concatenate text files as `=== path ===` blocks with line numbers; skips binaries and oversized files."""
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Project directory not found: {root}")
    blocks, total = [], 0
    for path in iter_project_files(root):
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        numbered = "\n".join(f"{i:>4} {line}" for i, line in enumerate(text.splitlines(), 1))
        block = f"=== {path.relative_to(root)} ===\n{numbered}\n"
        if total + len(block) > max_total:
            blocks.append("=== (remaining files omitted: size limit) ===\n")
            break
        blocks.append(block)
        total += len(block)
    if not blocks:
        raise ValueError(f"No readable text files in {root}")
    return "\n".join(blocks)
