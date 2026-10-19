from langchain.agents import create_agent


from llm.factory import get_llm
from agent.tools import search_codebase
from memory.short_term import get_checkpointer, get_summarization_middleware
from observability.logger import get_logger


logger = get_logger(__name__)


SYSTEM_PROMPT = """You are a senior software engineer with deep knowledge of the codebase.
Always use the search_codebase tool before answering any question.
Reference specific file names, function names and line numbers in your answers.
If you cannot find the answer in the codebase, say so explicitly."""


def build_agent():
  """Create a codebase-search agent that persists conversation state."""
  llm = get_llm()
  tools = [search_codebase]
  checkpointer = get_checkpointer()
  middleware = get_summarization_middleware()
  logger.info("Creating agent")
  return create_agent(
      llm,
      tools=tools,
      system_prompt=SYSTEM_PROMPT,
      checkpointer=checkpointer,
      middleware=[middleware],
  )
