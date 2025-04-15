import logging
import shutil
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

from pydantic import BaseModel

# Local imports
from .core.config import UPLOADED_FILES_DIR
from .services import document_processor, vector_store_manager, rag_pipeline

# Setup logging for log messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI(
    title="BeautiRAG API",
    description="API for handling document processing, embeddings, and RAG queries.",
    version="0.1.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Allow Next.js frontend
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"message": "BeautiRAG API is running!"}

@app.post("/upload/", tags=["Documents"])
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Uploads one or more documents, processes them, and adds them to the vector store.
    """
    processed_files_count = 0
    failed_files = []
    all_processed_docs = []

    for file in files:
        try:
            # Ensure upload directory exists
            UPLOADED_FILES_DIR.mkdir(parents=True, exist_ok=True)

            # Create a safe filepath
            file_location = UPLOADED_FILES_DIR / file.filename
            logger.info(f"Attempting to save uploaded file to: {file_location}")

            # Save the uploaded file
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
            logger.info(f"Successfully saved uploaded file: {file.filename}")

            # Process the saved document
            logger.info(f"Processing document: {file.filename}")
            processed_docs = document_processor.load_and_process_document(file_location)

            if processed_docs:
                all_processed_docs.extend(processed_docs)
                processed_files_count += 1
                logger.info(f"Successfully processed {file.filename}, found {len(processed_docs)} sections.")
            else:
                logger.warning(f"No content extracted from {file.filename}.")
                # Add to failed_files if partial success isn't desired
                failed_files.append(file.filename)

        except Exception as e:
            logger.error(f"Failed to process file {file.filename}: {e}", exc_info=True)
            failed_files.append(file.filename)
            # Clean up saved file if processing failed
            if file_location.exists():
                file_location.unlink()


    # Add all successfully processed documents to the vector store at once
    if all_processed_docs:
        try:
            logger.info(f"Adding {len(all_processed_docs)} document sections from {processed_files_count} file(s) to vector store.")
            vector_store_manager.add_documents_to_store(all_processed_docs)
            logger.info("Successfully updated vector store.")
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}", exc_info=True)
            # Return partial success but indicate store update failure
            return HTTPException(status_code=500, detail=f"Files processed, but failed to update vector store: {e}")

    if not processed_files_count and failed_files:
         raise HTTPException(status_code=500, detail=f"Failed to process all uploaded files: {', '.join(failed_files)}")

    return {
        "message": f"Processed {processed_files_count} file(s) successfully.",
        "processed_files": processed_files_count,
        "failed_files": failed_files,
    }


class QueryRequest(BaseModel):
    query: str
    model_name: Optional[str] = "gpt-4o"
    api_key: Optional[str] = None

@app.post("/query/", tags=["RAG"])
async def query_documents(request: QueryRequest):
    """
    Receives a query and returns the response from the RAG pipeline.
    """
    logger.info(f"Received query: '{request.query}' for model '{request.model_name}'")
    try:
        response = rag_pipeline.query_rag(
            query=request.query,
            model_name=request.model_name,
            api_key=request.api_key
        )
        logger.info(f"Generated response: '{response[:100]}...'")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error during RAG query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during the query: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 