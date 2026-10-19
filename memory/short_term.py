import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.agents.middleware import SummarizationMiddleware
from pathlib import Path


from config import config
from llm.factory import get_llm
from observability.logger import get_logger


logger = get_logger(__name__)


def get_checkpointer() -> SqliteSaver:
   """Open the configured SQLite database for persistent agent checkpoints."""
   db_path = config["memory"]["db_path"]
   Path(db_path).parent.mkdir(parents=True, exist_ok=True)
   logger.info(f"Using SQLite checkpointer at {db_path}")
   conn = sqlite3.connect(db_path, check_same_thread=False)
   return SqliteSaver(conn)


def get_session_history(thread_id: str) -> list[dict[str, str]]:
   """Load a session's saved checkpoint messages as user/assistant history."""
   checkpointer = get_checkpointer()
   checkpoint = checkpointer.get({"configurable": {"thread_id": thread_id}})
   if checkpoint is None:
       return []

   messages = checkpoint["channel_values"].get("messages", [])
   return [
       {
           "role": "user" if message.type == "human" else "assistant",
           "content": message.content,
       }
       for message in messages
   ]


def get_summarization_middleware() -> SummarizationMiddleware:
   """Create middleware that summarizes long histories and retains recent messages."""
   return SummarizationMiddleware(
       model=get_llm(),
       trigger=("tokens", config["memory"]["summarize_at_tokens"]),
       keep=("messages", config["memory"]["keep_last_messages"]),
   )
