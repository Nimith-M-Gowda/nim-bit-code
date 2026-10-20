from langchain.agents import create_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


from llm.factory import get_llm
from memory.short_term import get_summarization_middleware
from observability.logger import get_logger
from tools.terminal_tools import run_command, run_in_directory
from tools.search_tools import search_codebase
from integrations.mcp.client import get_mcp_tools


logger = get_logger(__name__)


SYSTEM_PROMPT = """You are a senior software engineer with deep knowledge of the codebase.
Always use the search_codebase tool before answering any question.
Reference specific file names, function names and line numbers in your answers.
If you cannot find the answer in the codebase, say so explicitly.
Use run_command or run_in_directory only for permitted read-only project inspection.
Use configured MCP tools for external integrations only when relevant, and make changes only when explicitly requested."""


async def build_agent(checkpointer: AsyncSqliteSaver):
  """Create and return a LangChain agent with persistent memory."""
  llm = get_llm()
  mcp_tools = await get_mcp_tools()
  tools = [
      search_codebase,
      run_command,
      run_in_directory,
      *mcp_tools,
  ]
  middleware = get_summarization_middleware(llm)
  logger.info("Creating agent")
  return create_agent(
      llm,
      tools=tools,
      system_prompt=SYSTEM_PROMPT,
      checkpointer=checkpointer,
      middleware=[middleware],
  )
