import logging
from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.config import FAISS_INDEX_DIR, EMBEDDING_MODEL_NAME

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FAISS_INDEX_FILE = FAISS_INDEX_DIR / "beautirag_index.faiss"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# --- Global Variables (Cached) ---
_embed_model: Optional[HuggingFaceEmbeddings] = None
_vector_store: Optional[FAISS] = None

def _get_embedding_model() -> HuggingFaceEmbeddings:
    """Initializes and returns the embedding model, caching it globally."""
    global _embed_model
    if _embed_model is None:
        logger.info(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}")
        _embed_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'}
        )
        logger.info("Embedding model initialized.")
    return _embed_model

def _split_documents(documents: List[Document]) -> List[Document]:
    """Splits documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def get_vector_store() -> Optional[FAISS]:
    """Loads the FAISS vector store from disk if it exists, otherwise returns None."""
    global _vector_store
    if _vector_store is None:
        if FAISS_INDEX_FILE.exists():
            try:
                embedding_model = _get_embedding_model()
                logger.info(f"Loading existing FAISS index from: {FAISS_INDEX_FILE}")
                _vector_store = FAISS.load_local(
                    str(FAISS_INDEX_DIR),
                    embeddings=embedding_model,
                    index_name="beautirag_index",
                    allow_dangerous_deserialization=True
                )
                logger.info("FAISS index loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}", exc_info=True)
                _vector_store = None
        else:
            logger.info(f"FAISS index not found at {FAISS_INDEX_FILE}. A new store will be created when documents are added.")
            _vector_store = None
    return _vector_store

def add_documents_to_store(documents: List[Document]):
    """Splits documents, generates embeddings, and adds them to the FAISS store, saving the result."""
    if not documents:
        logger.warning("No documents provided to add to the vector store.")
        return

    global _vector_store
    embedding_model = _get_embedding_model()
    chunks = _split_documents(documents)

    try:
        if _vector_store is None:
            # Create a new store if it doesn't exist
            logger.info("Creating a new FAISS vector store.")
            _vector_store = FAISS.from_documents(chunks, embedding_model)
            logger.info("New FAISS store created.")
        else:
            # Add documents to the existing store
            logger.info(f"Adding {len(chunks)} chunks to the existing FAISS store.")
            _vector_store.add_documents(chunks)
            logger.info("Chunks added to the existing store.")

        # Save the updated index
        logger.info(f"Saving FAISS index to: {FAISS_INDEX_FILE}")
        _vector_store.save_local(str(FAISS_INDEX_DIR), index_name="beautirag_index")
        logger.info("FAISS index saved successfully.")

    except Exception as e:
        logger.error(f"Failed to add documents or save FAISS index: {e}", exc_info=True)

# Initialize store on load
get_vector_store()

if __name__ == '__main__':
    # Test code (todo further...)
    pass