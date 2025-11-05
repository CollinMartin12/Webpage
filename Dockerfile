FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set permissions for wait script
RUN chmod +x /app/wait-for-db.sh

# Expose port
EXPOSE 5000

# Use the wait script as entrypoint
ENTRYPOINT ["/app/wait-for-db.sh"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
