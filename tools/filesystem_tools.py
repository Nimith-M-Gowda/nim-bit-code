from pathlib import Path

from langchain.tools import tool


_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
_MAX_OUTPUT_CHARS = 20_000


def _workspace_root() -> Path:
    """Return the resolved project root used to constrain filesystem access."""
    return Path.cwd().resolve()


def _resolve_path(file_path: str, *, must_exist: bool) -> Path:
    """Resolve a path and reject it unless it stays within the project root."""
    root = _workspace_root()
    path = Path(file_path)
    if not path.is_absolute():
        path = root / path

    resolved = path.resolve(strict=must_exist)
    if not resolved.is_relative_to(root):
        raise ValueError("path must be inside the project directory")
    return path


def _check_file_size(path: Path, additional_bytes: int = 0) -> int:
    """Ensure the current and prospective file size do not exceed the limit."""
    size = path.stat().st_size if path.exists() else 0
    if size + additional_bytes > _MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"file too large ({size + additional_bytes} bytes). "
            f"Max allowed is {_MAX_FILE_SIZE_BYTES} bytes"
        )
    return size


@tool
def read_file(file_path: str) -> str:
    """Read a UTF-8 text file inside the project, up to 10 MB."""
    if not file_path or not file_path.strip():
        return "Error: file path cannot be empty"

    try:
        path = _resolve_path(file_path, must_exist=True)
        if not path.is_file():
            return f"Error: path is not a file: {file_path}"
        _check_file_size(path)
        with path.open("rb") as file:
            content = file.read(_MAX_FILE_SIZE_BYTES + 1)
        if len(content) > _MAX_FILE_SIZE_BYTES:
            return f"Error: file exceeds the {_MAX_FILE_SIZE_BYTES} byte limit"
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return f"Error: file is not valid UTF-8 text: {file_path}"
    except ValueError as exc:
        return f"Error: {exc}"
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except FileNotFoundError:
        return f"Error: file not found: {file_path}"
    except OSError as exc:
        return f"Error: could not read file: {exc}"


@tool
def write_file(file_path: str, content: str) -> str:
    """Write UTF-8 text to a project file, creating parent directories if needed."""
    if not file_path or not file_path.strip():
        return "Error: file path cannot be empty"
    if len(content.encode("utf-8")) > _MAX_FILE_SIZE_BYTES:
        return f"Error: content exceeds the {_MAX_FILE_SIZE_BYTES} byte limit"

    try:
        path = _resolve_path(file_path, must_exist=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        _resolve_path(str(path.parent), must_exist=True)
        path = _resolve_path(str(path), must_exist=False)
        if path.exists() and not path.is_file():
            return f"Error: path is not a file: {file_path}"
        with path.open("w", encoding="utf-8") as file:
            file.write(content)
        return f"Written to {file_path}"
    except ValueError as exc:
        return f"Error: {exc}"
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except OSError as exc:
        return f"Error: could not write file: {exc}"


@tool
def append_file(file_path: str, content: str) -> str:
    """Append UTF-8 text to an existing project file, up to 10 MB total."""
    if not file_path or not file_path.strip():
        return "Error: file path cannot be empty"

    try:
        path = _resolve_path(file_path, must_exist=True)
        if not path.is_file():
            return f"Error: path is not a file: {file_path}"
        _check_file_size(path, len(content.encode("utf-8")))
        with path.open("a", encoding="utf-8") as file:
            file.write(content)
        return f"Appended to {file_path}"
    except ValueError as exc:
        return f"Error: {exc}"
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except FileNotFoundError:
        return f"Error: file not found: {file_path}"
    except OSError as exc:
        return f"Error: could not append to file: {exc}"


@tool
def delete_file(file_path: str) -> str:
    """Delete one file inside the project; directories cannot be deleted."""
    if not file_path or not file_path.strip():
        return "Error: file path cannot be empty"

    try:
        path = _resolve_path(file_path, must_exist=True)
        if not path.is_file():
            return f"Error: path is not a file: {file_path}"
        path.unlink()
        return f"Deleted {file_path}"
    except ValueError as exc:
        return f"Error: {exc}"
    except PermissionError:
        return f"Error: permission denied: {file_path}"
    except FileNotFoundError:
        return f"Error: file not found: {file_path}"
    except OSError as exc:
        return f"Error: could not delete file: {exc}"


@tool
def list_directory(directory: str) -> str:
    """List entries in a directory inside the project."""
    if not directory or not directory.strip():
        return "Error: directory cannot be empty"

    try:
        path = _resolve_path(directory, must_exist=True)
        if not path.is_dir():
            return f"Error: path is not a directory: {directory}"
        entries = sorted(entry.name for entry in path.iterdir())
        output = "\n".join(entries) if entries else "(empty directory)"
        if len(output) > _MAX_OUTPUT_CHARS:
            output = output[:_MAX_OUTPUT_CHARS] + "\n... output truncated"
        return output
    except ValueError as exc:
        return f"Error: {exc}"
    except PermissionError:
        return f"Error: permission denied: {directory}"
    except FileNotFoundError:
        return f"Error: directory not found: {directory}"
    except OSError as exc:
        return f"Error: could not list directory: {exc}"


@tool
def file_exists(file_path: str) -> str:
    """Check whether a path inside the project exists."""
    if not file_path or not file_path.strip():
        return "Error: file path cannot be empty"

    try:
        path = _resolve_path(file_path, must_exist=False)
        return str(path.exists())
    except ValueError as exc:
        return f"Error: {exc}"
    except OSError as exc:
        return f"Error: could not check path: {exc}"