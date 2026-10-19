from config import config
from observability.logger import get_logger


logger = get_logger(__name__)

def get_retriever():
   mode = config["rag"]["mode"]
   provider = config["vector_store"]["provider"]

   if mode not in {"semantic", "hybrid"}:
       raise ValueError(f"Unsupported RAG mode: {mode}")
   if provider == "qdrant":
       if mode == "hybrid":
           from .hybrid_qdrant import retrieve
       else:
           from .semantic_qdrant import retrieve
   elif provider == "chroma" and mode == "semantic":
       from .semantic_chroma import retrieve
   elif provider == "chroma":
       raise ValueError("Hybrid RAG mode is only supported with the Qdrant vector store")
   else:
       raise ValueError(f"Unsupported vector store provider: {provider}")

   return retrieve
