FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download textblob corpora
RUN python -m textblob.download_corpora

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "main.py"]
