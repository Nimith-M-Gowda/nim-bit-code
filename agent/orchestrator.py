from functools import lru_cache

from agent.factory import build_agent
from observability.logger import get_logger


logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_agent():
   """Build the application agent once and reuse it for subsequent questions."""
   return build_agent()


def handle_query(question: str, thread_id: str) -> str:
   """Ask the codebase agent a question within the specified persistent session."""
   logger.info(f"Handling query for session {thread_id}: {question}")
   agent = _get_agent()
   agent_config = {"configurable": {"thread_id": thread_id}}
   response = agent.invoke(
       {"messages": [{"role": "user", "content": question}]},
       agent_config,
   )
   return response["messages"][-1].content
