import os
import shlex
import subprocess
from pathlib import Path

from langchain.tools import tool

from observability.logger import get_logger


logger = get_logger(__name__)

_TIMEOUT_SECONDS = 30
_MAX_OUTPUT_CHARS = 20_000
_FILE_COMMANDS = {"cat", "head", "ls", "tail", "wc"}
_GIT_COMMANDS = {"diff", "log", "status"}


def _workspace_root() -> Path:
    """Return the resolved project root used to constrain terminal access."""
    return Path.cwd().resolve()


def _resolve_workspace_path(value: str, root: Path) -> Path:
    """Resolve a path and reject it unless it stays within the project root."""
    path = Path(value)
    if not path.is_absolute():
        path = root / path

    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError("path must be inside the project directory")
    return resolved


def _parse_command(command: str, root: Path) -> list[str]:
    """Parse and validate an allowed read-only command without invoking a shell."""
    if not command or not command.strip():
        raise ValueError("command cannot be empty")

    try:
        args = shlex.split(command)
    except ValueError as exc:
        raise ValueError(f"invalid command syntax: {exc}") from exc

    executable = args[0]
    if executable == "pwd" and len(args) == 1:
        return args

    if executable in _FILE_COMMANDS:
        paths = args[1:]
        if executable != "ls" and not paths:
            raise ValueError(f"{executable} requires at least one project file")
        resolved_paths = []
        for path in paths:
            if path.startswith("-"):
                raise ValueError("command options are not allowed")
            resolved_paths.append(str(_resolve_workspace_path(path, root)))
        return [executable, *resolved_paths]

    if executable == "rg":
        if len(args) < 2:
            raise ValueError("rg requires a search pattern")
        if args[1].startswith("-"):
            raise ValueError("rg options are not allowed")
        paths = args[2:]
        if paths and paths[0] == "--":
            paths = paths[1:]
        resolved_paths = []
        for path in paths:
            if path.startswith("-"):
                raise ValueError("rg options are not allowed")
            resolved_paths.append(str(_resolve_workspace_path(path, root)))
        return ["rg", "--", args[1], *resolved_paths]

    if executable == "git" and len(args) == 2 and args[1] in _GIT_COMMANDS:
        if args[1] == "diff":
            return [*args, "--no-ext-diff", "--no-textconv"]
        return args

    allowed = ", ".join(
        ["pwd", "ls", "cat", "head", "tail", "wc", "rg", "git status", "git diff", "git log"]
    )
    raise ValueError(f"command is not allowed; permitted commands: {allowed}")


def _format_result(result: subprocess.CompletedProcess[str]) -> str:
    """Combine process output and status into a bounded user-facing string."""
    parts = []
    if result.stdout:
        parts.append(result.stdout.rstrip())
    if result.stderr:
        parts.append(f"STDERR: {result.stderr.rstrip()}")
    if result.returncode != 0:
        parts.append(f"Exit code: {result.returncode}")

    output = "\n".join(parts) if parts else "(no output)"
    if len(output) > _MAX_OUTPUT_CHARS:
        output = output[:_MAX_OUTPUT_CHARS] + "\n... output truncated"
    return output


def _run(command: str, cwd: Path) -> str:
    """Run a validated command from a project directory with a timeout."""
    root = _workspace_root()
    if not cwd.is_relative_to(root):
        return "Error: working directory must be inside the project directory"

    try:
        args = _parse_command(command, root)
        logger.info("Running permitted terminal command: %s", args[0])
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
            env={
                **os.environ,
                "GIT_PAGER": "cat",
                "PAGER": "cat",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.fsmonitor",
                "GIT_CONFIG_VALUE_0": "false",
            },
        )
    except ValueError as exc:
        return f"Error: {exc}"
    except FileNotFoundError as exc:
        return f"Error: {exc}"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {_TIMEOUT_SECONDS} seconds"
    except OSError as exc:
        return f"Error: could not run command: {exc}"

    return _format_result(result)


@tool
def run_command(command: str) -> str:
    """Run an allowed read-only project inspection command from the project root."""
    return _run(command, _workspace_root())


@tool
def run_in_directory(command: str, directory: str) -> str:
    """Run an allowed read-only inspection command in a directory inside the project."""
    if not directory or not directory.strip():
        return "Error: directory cannot be empty"

    try:
        cwd = _resolve_workspace_path(directory, _workspace_root())
    except (FileNotFoundError, OSError, ValueError) as exc:
        return f"Error: invalid project directory: {exc}"

    if not cwd.is_dir():
        return f"Error: path is not a directory: {directory}"
    return _run(command, cwd)