FROM --platform=linux/amd64 python:3.10-slim
# FROM --platform=linux/arm64 python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    freetds-dev \
    freetds-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY ./pyproject.toml ./setup.py ./README.md /app/
COPY ./src /app/src

# Check if assets directory exists and copy if it does
COPY ./assets /app/assets

# Install the package with all dependencies
RUN pip install --no-cache-dir -e ".[all]"

# Expose the Streamlit port
EXPOSE 8501

# Create entrypoint script
RUN echo '#!/bin/bash\nstreamlit run src/main.py --server.port=8501 --server.address=0.0.0.0' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]