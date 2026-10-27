import os
from crewai.tools import tool

class FileTools:
    @tool("write_file")
    def write_file(filename: str, content: str) -> str:
        """
        Writes content to a specific file.
        Useful for saving code, design docs, or test suites.
        Args:
            filename: The name of the file (e.g., 'app.py' or 'tests/test_app.py').
            content: The full string content to write into the file.
        """
        # Create a directory for outputs if it doesn't exist
        os.makedirs("output", exist_ok=True)

        filepath = os.path.join("output", filename)

        # Ensure subdirectories within 'output' are created (e.g., output/tests/...)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            with open(filepath, "w") as f:
                f.write(content)
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Failed to write file: {str(e)}"
