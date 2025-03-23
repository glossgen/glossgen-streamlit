# GlossGen

GlossGen is an AI-powered data exploration and glossary generation tool that helps users understand and document their databases.

## Contribute
We welcome contributions to GlossGen! Whether you're fixing bugs, adding features, improving documentation, or suggesting enhancements, your help is appreciated.

### How to Contribute

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Environment

The project uses Docker for consistent development environments. To get started:


## Features

- Connect to multiple database types (MySQL, PostgreSQL, SQL Server)
- Explore database schema and table contents
- Generate comprehensive data glossaries with AI assistance
- Export glossaries to Excel format
- Save and load sessions for continued work

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/glossgen.git
cd glossgen

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

## Docker Deployment

GlossGen can be easily deployed using Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/glossgen.git
cd glossgen

# Create and configure the .env file
cp glossgen/.env.example .env
# Edit the .env file with your configuration

# Run the deployment script
chmod +x deploy-glossgen.sh
./deploy-glossgen.sh

# Or deploy manually
docker-compose -f docker-compose.yml up -d
```

For detailed deployment instructions, see the [Docker Deployment Guide](glossgen/README.md#docker-deployment).

## Cloud Deployment

GlossGen can also be deployed to cloud platforms:

### Google Cloud Run

```bash
# Deploy to Google Cloud Run
chmod +x deploy-to-cloud-run.sh
./deploy-to-cloud-run.sh
```

For detailed Cloud Run deployment instructions, see the [Google Cloud Run Deployment Guide](glossgen/README.md#deploying-to-google-cloud-run).

## License

This project is licensed under the Business Source License 1.1 (BSL). 

This means:
- You are free to use, modify, and distribute the software for any non-commercial purpose
- You cannot use the software for a "Database Service" (as defined in the license)
- Commercial use requires a license from the copyright holders
- After four years, the software automatically converts to Apache License 2.0

The BSL is a source-available license that provides open-source-like freedoms while allowing the original developers to maintain commercial rights to the software.

For commercial licensing inquiries, please contact info@glossgen.ai.

See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact info@glossgen.ai.
