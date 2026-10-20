from langchain_core.messages import AIMessage, RemoveMessage, ToolMessage

from observability.logger import get_logger


logger = get_logger(__name__)


async def _remove_incomplete_tool_calls(agent, agent_config: dict) -> None:
   """Remove failed tool-call turns before resending history to the model."""
   state = await agent.aget_state(agent_config)
   messages = state.values.get("messages", [])
   removals: dict[str, RemoveMessage] = {}

   for index, message in enumerate(messages):
       if not isinstance(message, AIMessage) or not message.tool_calls:
           continue

       expected_ids = {tool_call["id"] for tool_call in message.tool_calls}
       result_ids = set()
       for following in messages[index + 1:]:
           if not isinstance(following, ToolMessage):
               break
           if following.tool_call_id in expected_ids:
               result_ids.add(following.tool_call_id)

       if expected_ids <= result_ids:
           continue

       if message.id is None:
           raise ValueError("Cannot repair an incomplete tool call without a message ID")
       removals[message.id] = RemoveMessage(id=message.id)
       for candidate in messages[index + 1:]:
           if isinstance(candidate, ToolMessage) and candidate.tool_call_id in expected_ids:
               if candidate.id is None:
                   raise ValueError("Cannot repair a tool result without a message ID")
               removals[candidate.id] = RemoveMessage(id=candidate.id)

   if removals:
       logger.warning("Removing %s messages from an incomplete tool-call turn", len(removals))
       await agent.aupdate_state(agent_config, {"messages": list(removals.values())})


async def handle_query(agent, question: str, thread_id: str) -> str:
   """Invoke the provided agent within the specified persistent session."""
   logger.info(f"Handling query for session {thread_id}: {question}")
   agent_config = {"configurable": {"thread_id": thread_id}}
   await _remove_incomplete_tool_calls(agent, agent_config)
   response = await agent.ainvoke(
       {"messages": [{"role": "user", "content": question}]},
       agent_config,
   )
   return response["messages"][-1].content
