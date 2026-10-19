from config import config
from observability.logger import get_logger


logger = get_logger(__name__)


def get_indexer():
   mode = config["rag"]["mode"]
   provider = config["vector_store"]["provider"]

   if mode not in {"semantic", "hybrid"}:
       raise ValueError(f"Unsupported RAG mode: {mode}")
   if provider == "qdrant":
       if mode == "hybrid":
           from .hybrid_qdrant import index_codebase
       else:
           from .semantic_qdrant import index_codebase
   elif provider == "chroma" and mode == "semantic":
       from .semantic_chroma import index_codebase
   elif provider == "chroma":
       raise ValueError("Hybrid RAG mode is only supported with the Qdrant vector store")
   else:
       raise ValueError(f"Unsupported vector store provider: {provider}")

   return index_codebase


def get_index_inspector():
   """Return the right show_index function based on rag mode and vector_store in config."""
   mode = config["rag"]["mode"]
   provider = config["vector_store"]["provider"]


   if mode not in {"semantic", "hybrid"}:
       raise ValueError(f"Unsupported RAG mode: {mode}")
   if provider == "qdrant":
       if mode == "hybrid":
           from .hybrid_qdrant import show_index
       else:
           from .semantic_qdrant import show_index
   elif provider == "chroma" and mode == "semantic":
       from .semantic_chroma import show_index
   elif provider == "chroma":
       raise ValueError("Hybrid RAG mode is only supported with the Qdrant vector store")
   else:
       raise ValueError(f"Unsupported vector store provider: {provider}")

   return show_index
