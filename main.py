from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt


from config import config
from context.indexers.factory import get_indexer, get_index_inspector
from agent.orchestrator import handle_query
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


def initialize():
   """Load the code index and active session before the REPL starts."""
   console.print(f"[dim]LLM: {config['llm']['provider']} / {config['llm']['model']}[/dim]")
   console.print(f"[dim]Embedder: {config['embeddings']['provider']} / {config['embeddings']['model']}[/dim]")


   index = get_or_create_index()
   session_id = get_current_session()
   console.print(f"[dim]Session: {session_id}[/dim]")
   console.print(f"[green]✓ Ready[/green]\n")
   return index, session_id


def run():
   """Run the interactive REPL for code questions and session management."""
   logger.info("Starting nim-bit-code")
   console.print("\n[bold blue]nim-bit-code[/bold blue] — RAG-powered code assistant")


   index, session_id = initialize()
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
           response = handle_query(question, session_id)
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


if __name__ == "__main__":
   run()
