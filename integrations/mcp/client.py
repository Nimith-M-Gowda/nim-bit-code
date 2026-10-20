from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.runnables import RunnableConfig

from observability.logger import get_logger
from integrations.mcp.config import load_mcp_configs


logger = get_logger(__name__)


def _return_tool_errors(tool: BaseTool) -> StructuredTool:
    """Turn MCP failures into explicit tool results so model history stays valid."""
    async def invoke(config: RunnableConfig, **tool_input):
        try:
            result = await tool.arun(
                tool_input,
                config=config,
                tool_call_id="mcp-wrapper-call",
            )
            if tool.response_format == "content_and_artifact":
                if not isinstance(result, ToolMessage):
                    raise TypeError(
                        f"MCP tool {tool.name} returned {type(result).__name__}, "
                        "expected a ToolMessage containing content and artifact"
                    )
                return result.content, result.artifact
            return result
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            logger.warning("MCP tool %s failed: %s", tool.name, error)
            if tool.response_format == "content_and_artifact":
                return f"MCP tool failed: {error}", {"error": error}
            return f"MCP tool failed: {error}"

    return StructuredTool.from_function(
        coroutine=invoke,
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        return_direct=tool.return_direct,
        response_format=tool.response_format,
        metadata=tool.metadata,
        tags=tool.tags,
        callbacks=tool.callbacks,
        verbose=tool.verbose,
    )


async def get_mcp_tools() -> list:
    """Connect to configured MCP servers and return their LangChain tools."""
    configs = load_mcp_configs()
    logger.info("Loading tools from MCP servers: %s", list(configs))
    client = MultiServerMCPClient(configs)
    tools = [_return_tool_errors(tool) for tool in await client.get_tools()]
    logger.info("Loaded %s tools from configured MCP servers", len(tools))
    return tools
