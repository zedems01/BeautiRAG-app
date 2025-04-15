import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Core Paths ---
BACKEND_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BACKEND_DIR.parent
APP_DIR = SRC_DIR.parent
WORKSPACE_DIR = APP_DIR.parent

# --- Data Storage Paths ---
DATA_DIR = BACKEND_DIR / "data"
UPLOADED_FILES_DIR = DATA_DIR / "uploaded_files"
PROCESSED_FILES_DIR = DATA_DIR / "processed_files"
FAISS_INDEX_DIR = DATA_DIR / "faiss_index"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADED_FILES_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_FILES_DIR.mkdir(parents=True, exist_ok=True)
FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)


# --- Whisper Configuration ---
# Model size (e.g., "tiny", "base") Larger models may require more resources
# NOT RECOMMANDED ("small", "medium", "large-v1", "large-v2", "large-v3")
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

# --- Embedding Model Configuration ---
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# --- LLM Configuration ---
SELECTED_LLM = os.getenv("SELECTED_LLM", "default_local_llm")
# Load API keys if needed (not necessary for at this stage)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

print(f"Workspace Dir: {WORKSPACE_DIR}")
print(f"App Dir: {APP_DIR}")
print(f"Backend Dir: {BACKEND_DIR}")
print(f"Data Dir: {DATA_DIR}")
print(f"Uploaded Files Dir: {UPLOADED_FILES_DIR}")
print(f"Processed Files Dir: {PROCESSED_FILES_DIR}")
print(f"FAISS Index Dir: {FAISS_INDEX_DIR}") 