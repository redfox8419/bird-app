# Use slim Python image
FROM python:3.10-slim

# Install OS deps (ffmpeg for audio I/O)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your server code
COPY main.py .

# Use PORT env var provided by Render
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:$PORT", "--workers", "2"]
