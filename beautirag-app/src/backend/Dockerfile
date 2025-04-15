FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory to a level above the actual backend code
WORKDIR /app_root

# Create the backend directory structure
RUN mkdir -p ./backend

# System dependencies required for Tesseract, Whisper (ffmpeg), and potentially Unstructured
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    libmagic-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Rest of the backend application code into the backend subdirectory
COPY . ./backend/

EXPOSE 8000


CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 