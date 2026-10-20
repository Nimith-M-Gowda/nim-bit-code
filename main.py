import asyncio
from pathlib import Path

from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from rich.console import Console
from rich.prompt import Prompt

from config import config
from context.indexers.factory import get_indexer, get_index_inspector
from agent.factory import build_agent
from agent.orchestrator import handle_query
from memory.short_term import get_checkpointer
from memory.sessions import get_current_session, new_session, switch_session
from observability.logger import get_logger


# Load .env before anything else
load_dotenv(Path(__file__).parent / ".env")


console = Console()
logger = get_logger(__name__)


def get_or_create_index():
   """Load the configured code index for the repository in the current directory."""
   repo_path = str(Path.cwd())
   logger.info(f"Checking index for: {repo_path}")
   console.print(f"[dim]Checking index for {repo_path}...[/dim]")
   return get_indexer()(repo_path)


async def initialize(checkpointer: AsyncSqliteSaver):
   """Load the index, agent, and active session before the REPL starts."""
   console.print(f"[dim]LLM: {config['llm']['provider']} / {config['llm']['model']}[/dim]")
   console.print(f"[dim]Embedder: {config['embeddings']['provider']} / {config['embeddings']['model']}[/dim]")

   index = get_or_create_index()
   agent = await build_agent(checkpointer)
   session_id = get_current_session()
   console.print(f"[dim]Session: {session_id}[/dim]")
   console.print(f"[green]✓ Ready[/green]\n")
   return index, agent, session_id


async def _run():
   """Run the interactive REPL for code questions and session management."""
   logger.info("Starting nim-bit-code")
   console.print("\n[bold blue]nim-bit-code[/bold blue] — RAG-powered code assistant")

   async with get_checkpointer() as checkpointer:
       index, agent, session_id = await initialize(checkpointer)
       await _run_repl(agent, index, session_id)


async def _run_repl(agent, index, session_id: str) -> None:
   """Process REPL commands while reusing the agent and its live checkpointer."""
   console.print("Type [bold]'/exit'[/bold] to quit\n")


   while True:
       user_input = Prompt.ask("[bold green]>[/bold green]")


       if not user_input.strip():
           continue
       if user_input.lower() in ("/exit", "/quit"):
           logger.info("Shutting down")
           console.print("[dim]Goodbye![/dim]")
           break
       elif user_input.startswith("/ask "):
           question = user_input.removeprefix("/ask ").strip()
           logger.info(f"Ask command received: {question}")
           console.print(f"[dim]Searching for: {question}...[/dim]")
           try:
               response = await handle_query(agent, question, session_id)
           except Exception:
               logger.exception("Query failed")
               console.print(
                   "[red]The request failed. Check the application log for details, "
                   "then retry or start a new session with /new_session.[/red]"
               )
           else:
               console.print(response)
       elif user_input == "/new_session":
           session_id = new_session()
           console.print(f"[green]New session started: {session_id}[/green]")
       elif user_input.startswith("/switch "):
           target_session_id = user_input.removeprefix("/switch ").strip()
           if not target_session_id:
               console.print("[yellow]Usage: /switch <session_id>[/yellow]")
               continue
           session_id = switch_session(target_session_id)
           console.print(f"[green]Switched to session: {session_id}[/green]")
       elif user_input == "/session":
           console.print(f"[dim]Current session: {session_id}[/dim]")
       elif user_input in ("/show_index", "/show_semantic_index"):
           logger.info("Showing index")
           get_index_inspector()(index)
       else:
           logger.warning(f"Unknown command received: {user_input}")
           console.print("[yellow]Unknown command. Try:[/yellow]")
           console.print("  [bold]/ask <question>[/bold]       — ask a question about the codebase")
           console.print("  [bold]/show_index[/bold]           — show all chunks in the index")
           console.print("  [bold]/new_session[/bold]          — start a fresh conversation")
           console.print("  [bold]/switch <session_id>[/bold]  — resume a past session")
           console.print("  [bold]/session[/bold]              — show the current session ID")


def run():
   """Start the asynchronous REPL event loop."""
   asyncio.run(_run())


if __name__ == "__main__":
   run()
