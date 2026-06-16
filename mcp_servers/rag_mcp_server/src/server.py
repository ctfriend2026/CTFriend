import os
import logging
from typing import List

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
#from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever

from fastmcp import FastMCP

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

KNOWLEDGE_BASE_DIR: str = "/app/knowledge_base"
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

retriever: VectorStoreRetriever = None

mcp = FastMCP(
    name="RAG Knowledge Base Server",
)

def setup_retriever() -> VectorStoreRetriever:
    """
    Loads documents from the knowledge base directory, processes them into a
    searchable vector store, and returns a retriever object.

    Returns:
        A configured LangChain VectorStoreRetriever, or None if an error occurs.
    """
    logger.info("Initializing RAG retriever setup with local embeddings...")

    if not os.path.isdir(KNOWLEDGE_BASE_DIR) or not os.listdir(KNOWLEDGE_BASE_DIR):
        logger.warning(
            f"Knowledge base directory '{KNOWLEDGE_BASE_DIR}' is empty or does not exist. "
            "RAG tool will be unavailable."
        )
        return None

    logger.info(f"Attempting to load documents from '{KNOWLEDGE_BASE_DIR}'")
    try:
        docs = []
        
        pdf_loader = DirectoryLoader(
            KNOWLEDGE_BASE_DIR,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            use_multithreading=True,
            show_progress=True,
        )
        docs.extend(pdf_loader.load())

        md_loader = DirectoryLoader(
            KNOWLEDGE_BASE_DIR,
            glob="**/*.md",
            loader_cls=TextLoader,
            use_multithreading=True,
            show_progress=True,
        )
        docs.extend(md_loader.load())

        if not docs:
            logger.warning("No documents were successfully loaded.")
            return None
        logger.info(f"Successfully loaded {len(docs)} documents.")
    except Exception as e:
        logger.error(f"Failed to load documents: {e}")
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    logger.info(f"Split documents into {len(splits)} chunks.")

    logger.info(f"Loading local embedding model: '{EMBEDDING_MODEL_NAME}'...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    logger.info("Embedding model loaded.")

    logger.info("Creating vector store...")
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    logger.info("Vector store created successfully.")
    
    return vectorstore.as_retriever()

@mcp.tool()
def query_knowledge_base(query: str) -> str:
    """
    Searches and returns relevant information from the local knowledge base.
    Use this for questions about internal documents, project specifics,
    or any stored markdown/pdf files.
    """
    global retriever
    if retriever is None:
        return "Error: The knowledge base retriever is not available or failed to initialize."
    
    logger.info(f"Querying knowledge base with: '{query}'")
    results = retriever.invoke(query)
    
    if not results:
        return "No relevant information found in the knowledge base."
        
    formatted_results = "\n\n---\n\n".join([doc.page_content for doc in results])
    return f"Found the following information in the knowledge base:\n\n{formatted_results}"

def main() -> None:
    global retriever
    logger.info("Starting RAG MCP Server setup...")
    retriever = setup_retriever()

    if retriever:
        logger.info("🚀 RAG server starting (SSE)...")
    else:
        logger.error("No retriever was created. The server will start with no active tools.")

    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port="8002"
    )

if __name__ == "__main__":
    main()
