import uuid
from pathlib import Path


from config import config
from observability.logger import get_logger


logger = get_logger(__name__)


def _session_file() -> Path:
   """Locate the file that stores the ID of the active conversation session."""
   return Path(config["memory"]["db_path"]).parent / "current_session"


def get_current_session() -> str:
   """Resume the saved conversation session, creating one if none is saved."""
   session_file = _session_file()
   if session_file.exists():
       session_id = session_file.read_text().strip()
       logger.info(f"Resuming session: {session_id}")
       return session_id
   return new_session()


def new_session() -> str:
   """Create and persist a fresh ID to start an independent conversation session."""
   session_id = str(uuid.uuid4())
   session_file = _session_file()
   session_file.parent.mkdir(parents=True, exist_ok=True)
   session_file.write_text(session_id)
   logger.info(f"Started new session: {session_id}")
   return session_id


def switch_session(session_id: str) -> str:
   """Make an existing session ID active so later memory operations use that session."""
   session_file = _session_file()
   session_file.write_text(session_id)
   logger.info(f"Switched to session: {session_id}")
   return session_id
