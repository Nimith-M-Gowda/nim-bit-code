from langchain.agents import create_agent


from llm.factory import get_llm
from agent.tools import search_codebase
from memory.short_term import get_checkpointer, get_summarization_middleware
from observability.logger import get_logger
from tools.filesystem_tools import (
    append_file,
    delete_file,
    file_exists,
    list_directory,
    read_file,
    write_file,
)
from tools.terminal_tools import run_command, run_in_directory


logger = get_logger(__name__)


SYSTEM_PROMPT = """You are a senior software engineer with deep knowledge of the codebase.
Always use the search_codebase tool before answering any question.
Reference specific file names, function names and line numbers in your answers.
If you cannot find the answer in the codebase, say so explicitly.
Use run_command or run_in_directory only for permitted read-only project inspection.
Use filesystem tools only within the project; delete files only when explicitly requested."""


def build_agent():
  """Create and return a LangChain agent with persistent memory."""
  llm = get_llm()
  tools = [
      search_codebase,
      run_command,
      run_in_directory,
      read_file,
      write_file,
      append_file,
      delete_file,
      list_directory,
      file_exists,
  ]
  checkpointer = get_checkpointer()
  middleware = get_summarization_middleware(llm)
  logger.info("Creating agent")
  return create_agent(
      llm,
      tools=tools,
      system_prompt=SYSTEM_PROMPT,
      checkpointer=checkpointer,
      middleware=[middleware],
  )
