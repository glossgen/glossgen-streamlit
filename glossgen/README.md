# GlossGen

GlossGen is an AI-powered data exploration and glossary generation tool that helps users understand and document their databases.

## Features

- Connect to multiple database types (MySQL, PostgreSQL, SQL Server)
- Explore database schema and table contents
- Generate comprehensive data glossaries with AI assistance
- Export glossaries to Excel format
- Save and load sessions for continued work

## Installation

```bash
# Install the package
pip install -e .

# For SQL Server support, install the optional dependency
pip install -e ".[mssql]"
```

## Usage

```bash
# Run the application
streamlit run src/main.py
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black .
isort .

# Type checking
mypy src/

# Run tests
pytest
```

## Project Structure

```
glossgen/
├── src/
│   ├── glossgen/
│   │   ├── config/       # Application configuration
│   │   ├── state/        # State management
│   │   ├── services/     # Database and AI services
│   │   ├── ui/           # UI components
│   │   ├── utils/        # Utility functions
│   │   ├── chains/       # LangChain components
│   │   └── tools/        # Custom tools
│   └── main.py           # Application entry point
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## License

Proprietary - All rights reserved.

## Docker Deployment

GlossGen can be easily deployed using Docker. Follow these steps to deploy the application:

### Prerequisites

- Docker and Docker Compose installed on your system
- OpenAI API key for AI-powered features

### Deployment Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/glossgen.git
   cd glossgen
   ```

2. Create a `.env` file based on the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your OpenAI API key and other configuration options:
   ```bash
   # Required for AI features
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Configure database connections as needed
   MYSQL_HOST=mysql_host
   MYSQL_PORT=3306
   # ... other configuration options
   ```

4. Build and start the Docker container:
   ```bash
   # Using the deployment script
   ./deploy-glossgen.sh
   
   # Or manually with docker-compose
   docker-compose -f docker-compose.yml up -d
   ```

5. Access the application at http://localhost:8501

### Environment Variables

The following environment variables can be configured in the `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key for AI-powered features (required for AI functionality)
- Database connection settings:
  - MySQL: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
  - PostgreSQL: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DATABASE`
  - SQL Server: `MSSQL_HOST`, `MSSQL_PORT`, `MSSQL_USER`, `MSSQL_PASSWORD`, `MSSQL_DATABASE`
- Application settings: `DEBUG`, `LOG_LEVEL`

### Docker Compose Configuration

The `docker-compose.yml` file includes:

- Building the application from the Dockerfile
- Mapping port 8501 for the Streamlit interface
- Mounting volumes for data persistence and live code updates
- Setting up environment variables from the `.env` file

### Managing the Docker Container

```bash
# Start the container
docker-compose -f docker-compose.yml up -d

# Stop the container
docker-compose -f docker-compose.yml down

# View logs
docker-compose -f docker-compose.yml logs

# Rebuild and restart after code changes
docker-compose -f docker-compose.yml up -d --build
```

### Troubleshooting

If you encounter any issues with the Docker deployment:

1. Check the container logs:
   ```bash
   docker-compose -f docker-compose.yml logs
   ```

2. Ensure your `.env` file contains the correct configuration.

3. Make sure ports are not already in use on your system:
   ```bash
   # Check if port 8501 is in use
   lsof -i :8501
   ```

4. Verify Docker is running properly:
   ```bash
   docker info
   ```

5. If you're having permission issues:
   ```bash
   # On Linux, you might need to run Docker commands with sudo
   sudo docker-compose -f docker-compose.yml up -d
   ```

6. Use the deployment check script to diagnose issues:
   ```bash
   ./check-glossgen-deployment.sh
   ```

### Production Deployment Considerations

For production deployments, consider the following:

1. Use a reverse proxy like Nginx to handle HTTPS and security:
   ```
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

2. Set up proper authentication for your application.

3. Configure regular backups of your data volume.

4. Consider using Docker Swarm or Kubernetes for high availability.

## Deploying to Google Cloud Run

GlossGen can be deployed to Google Cloud Run for a serverless, scalable deployment.

### Prerequisites

- Google Cloud account with billing enabled
- Google Cloud SDK (gcloud) installed
- Docker installed with buildx support

### Deployment Steps

1. Update the configuration variables in the `deploy-to-cloud-run.sh` script:
   ```bash
   PROJECT_ID="your-project-id"  # Your Google Cloud project ID
   REGION="your-region"          # Your preferred region
   SERVICE_NAME="glossgen"       # Name for your Cloud Run service
   REPOSITORY="chatdb"           # Artifact Registry repository name
   IMAGE_NAME="chatdb-glossgen"  # Image name
   ```

2. Run the deployment script:
   ```bash
   ./deploy-to-cloud-run.sh
   ```

3. The script will:
   - Authenticate with Google Cloud
   - Enable required services
   - Create an Artifact Registry repository
   - Build a multi-platform Docker image compatible with Cloud Run
   - Deploy the image to Cloud Run
   - Output the URL where your application is running

### Troubleshooting Cloud Run Deployment

If you encounter the error "Container manifest type must support amd64/linux":

1. Ensure you're building the image with the correct platform:
   ```bash
   docker build --platform linux/amd64 ...
   ```

2. Check that your Dockerfile specifies the platform:
   ```dockerfile
   FROM --platform=linux/amd64 python:3.10-slim
   ```

3. If you're using an M1/M2 Mac, make sure Docker Desktop has Rosetta enabled for x86/amd64 emulation.

If you encounter the error "Image not found":

1. Make sure the image is being properly pushed to the Artifact Registry:
   ```bash
   # Verify the image exists in the registry
   gcloud artifacts docker images list REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY \
       --filter="IMAGE_NAME"
   ```

2. Try building and pushing the image separately:
   ```bash
   # Build the image
   docker build --platform linux/amd64 -t REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE_NAME:TAG -f glossgen/Dockerfile .
   
   # Push the image
   docker push REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE_NAME:TAG
   ```

3. Check that you have the necessary permissions to push to the Artifact Registry and deploy to Cloud Run.

4. If you're still having issues, try using the updated `deploy-to-cloud-run.sh` script which includes additional error handling and verification steps. 