from pathlib import Path

from crewai.tools import tool

OUTPUT_DIR = Path("output")


def safe_write(filename: str, content: str, base_dir: Path = OUTPUT_DIR) -> str:
    """Write content to base_dir/filename, refusing paths that escape base_dir."""
    base = base_dir.resolve()
    target = (base / filename).resolve()
    if not target.is_relative_to(base) or target == base:
        return f"Refused to write '{filename}': path must stay inside {base_dir}/"
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Successfully wrote to {base_dir / target.relative_to(base)}"
    except OSError as e:
        return f"Failed to write file: {e}"


class FileTools:
    @tool("write_file")
    def write_file(filename: str, content: str) -> str:
        """
        Writes content to a file inside the output directory.
        Useful for saving code, design docs, or reports.
        Args:
            filename: Relative file name (e.g., 'Dockerfile' or 'docs/design.md').
            content: The full string content to write into the file.
        """
        return safe_write(filename, content)
