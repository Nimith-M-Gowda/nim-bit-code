from contextlib import AbstractAsyncContextManager
from pathlib import Path

from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


from config import config
from llm.factory import get_llm
from observability.logger import get_logger


logger = get_logger(__name__)


def get_checkpointer_db_path() -> str:
   """Create the memory directory and return the configured SQLite database path."""
   db_path = config["memory"]["db_path"]
   Path(db_path).parent.mkdir(parents=True, exist_ok=True)
   logger.info(f"Using SQLite checkpointer at {db_path}")
   return db_path


def get_checkpointer() -> AbstractAsyncContextManager[AsyncSqliteSaver]:
   """Return a context manager that owns the asynchronous SQLite connection."""
   return AsyncSqliteSaver.from_conn_string(get_checkpointer_db_path())


async def get_session_history(thread_id: str) -> list[dict[str, str]]:
   """Load a session's saved checkpoint messages as user/assistant history."""
   async with get_checkpointer() as checkpointer:
       checkpoint = await checkpointer.aget({"configurable": {"thread_id": thread_id}})
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


def get_summarization_middleware(
   model: BaseChatModel | None = None,
) -> SummarizationMiddleware:
   """Create middleware that summarizes long histories and retains recent messages."""
   return SummarizationMiddleware(
       model=model or get_llm(),
       trigger=("tokens", config["memory"]["summarize_at_tokens"]),
       keep=("messages", config["memory"]["keep_last_messages"]),
   )
