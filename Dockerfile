FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install the CLI tool (so `video-to-text` is available globally)
RUN pip install --no-cache-dir .

ENTRYPOINT ["video-to-text"]

CMD ["--help"]
