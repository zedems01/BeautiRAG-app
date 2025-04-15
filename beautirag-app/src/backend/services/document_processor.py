import os
from pathlib import Path
import logging
import uuid

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredFileLoader,
)
from langchain_core.documents import Document


import pytesseract
from PIL import Image
import whisper

from ..core.config import UPLOADED_FILES_DIR, PROCESSED_FILES_DIR, WHISPER_MODEL_SIZE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Whisper Model Loading ---
WHISPER_MODEL = None
def load_whisper_model():
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        try:
            logger.info(f"Loading Whisper model: {WHISPER_MODEL_SIZE}")
            WHISPER_MODEL = whisper.load_model(WHISPER_MODEL_SIZE)
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model '{WHISPER_MODEL_SIZE}': {e}", exc_info=True)
            WHISPER_MODEL = None

load_whisper_model()

# --- Helper Function to Save Processed Text ---
def save_processed_text(text_content: str, original_filename: str) -> Path:
    """Saves the extracted text content to a file in the processed directory."""
    base_name = Path(original_filename).stem
    # Use a unique identifier to prevent collisions if multiple files have the same name
    unique_id = uuid.uuid4().hex[:8]
    output_filename = f"{base_name}_{unique_id}.txt"
    output_path = PROCESSED_FILES_DIR / output_filename

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        logger.info(f"Saved processed text to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save processed text for {original_filename} to {output_path}: {e}")
        raise

# --- Image Processing (OCR) ---
def process_image(file_path: Path) -> list[Document]:
    """Extracts text from an image file using Tesseract OCR."""
    logger.info(f"Processing image file: {file_path}")
    try:
        text = pytesseract.image_to_string(Image.open(file_path))
        if not text.strip():
            logger.warning(f"No text found in image: {file_path}")
            return []

        saved_path = save_processed_text(text, file_path.name)
        # Create a LangChain Document object
        metadata = {"source": str(file_path.name), "processed_path": str(saved_path)}
        doc = Document(page_content=text, metadata=metadata)
        return [doc]
    except pytesseract.TesseractNotFoundError:
        logger.error(
            "Tesseract is not installed or not in the system's PATH. "
            "Please install Tesseract and configure the path if necessary. "
            "Skipping OCR for: {file_path}"
        )
        return []
    except Exception as e:
        logger.error(f"Error processing image {file_path}: {e}")
        return []


# --- Audio Processing (Transcription) ---
def process_audio(file_path: Path) -> list[Document]:
    """Transcribes an audio file using Whisper."""
    logger.info(f"Processing audio file: {file_path}")
    if WHISPER_MODEL is None:
        logger.error("Whisper model not loaded. Cannot process audio file: {file_path}")
        return []
    try:
        result = WHISPER_MODEL.transcribe(str(file_path), fp16=False) # fp16=False for CPU
        text = result['text']
        # logger.info(f"EXTRACTED TEXT:\n{text[:100]}")

        if not text.strip():
            logger.warning(f"No text transcribed from audio: {file_path}")
            return []

        saved_path = save_processed_text(text, file_path.name)
        metadata = {"source": str(file_path.name), "processed_path": str(saved_path)}
        doc = Document(page_content=text, metadata=metadata)
        # logger.info(f"LANGCHAIN FORMATED EXTRACTED TEXT:\n{doc.page_content}")
        return [doc]
    except Exception as e:
        logger.error(f"Error processing audio {file_path}: {e}", exc_info=True)
        if "ffmpeg" in str(e).lower():
             logger.error("FFmpeg might not be installed or found. Please ensure FFmpeg is installed and in your system PATH.")
        return []

# --- Document Loading and Processing Map ---
PROCESSOR_MAP = {
    ".pdf": UnstructuredFileLoader,
    ".txt": UnstructuredFileLoader,
    ".docx": UnstructuredFileLoader,
    ".png": process_image, 
    ".jpg": process_image,
    ".jpeg": process_image,
    ".mp3": process_audio,
    ".wav": process_audio,
    ".csv": CSVLoader,
    ".html": UnstructuredFileLoader,
}

def load_and_process_document(file_path: Path) -> list[Document]:
    """Loads a document using the appropriate LangChain loader based on its extension."""
    if not file_path.is_file():
        logger.error(f"File not found: {file_path}")
        return []

    file_ext = file_path.suffix.lower()
    logger.info(f"Attempting to process file: {file_path} with extension: {file_ext}")

    processor = PROCESSOR_MAP.get(file_ext)

    docs = []
    try:
        if processor:
            if isinstance(processor, type):
                logger.info(f"Using LangChain loader: {processor.__name__} for {file_path.name}")
                loader = processor(str(file_path))
                docs = loader.load()
                if docs:
                    full_text = "\n\n".join([doc.page_content for doc in docs])
                    save_processed_text(full_text, file_path.name)
                    for doc in docs:
                        doc.metadata["source"] = str(file_path.name)

            else:
                logger.info(f"Using custom processor for {file_path.name}")
                docs = processor(file_path)
        else:
            # For unsupported explicit types, trying generic Unstructured loader
            logger.warning(f"No specific loader for extension '{file_ext}'. Attempting generic UnstructuredFileLoader.")
            try:
                loader = UnstructuredFileLoader(str(file_path))
                docs = loader.load()
                if docs:
                    full_text = "\n\n".join([doc.page_content for doc in docs])
                    save_processed_text(full_text, file_path.name)
                    for doc in docs:
                         doc.metadata["source"] = str(file_path.name)
                else:
                     logger.warning(f"UnstructuredFileLoader could not extract content from {file_path.name}")
            except Exception as e:
                logger.error(f"UnstructuredFileLoader failed for {file_path.name}: {e}")
                docs = []

        if not docs:
            logger.warning(f"No documents extracted from file: {file_path}")

        logger.info(f"Successfully processed {file_path.name}. Extracted {len(docs)} document sections.")
        return docs

    except Exception as e:
        logger.error(f"Failed to load or process document {file_path}: {e}", exc_info=True)
        return []

if __name__ == '__main__':
    # Test code (todo further...)
    pass