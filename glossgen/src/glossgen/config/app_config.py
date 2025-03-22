import os
from typing import Dict, List

class AppConfig:
    """Application configuration settings"""
    
    # Page settings
    PAGE_TITLE = "GlossGen"
    PAGE_ICON = "🔍"
    PAGE_LAYOUT = "wide"
    
    # Database settings
    DB_TYPES = ["MySQL", "PostgreSQL", "SQLite", "MS SQL Server"]
    
    # AI provider settings
    DEFAULT_AI_PROVIDER = "OpenAI"
    AI_PROVIDERS = ["OpenAI", "Deepseek", "OpenAI Compatible", "Claude", "Google Gemini"]
    
    # AI model settings by provider
    AI_MODELS: Dict[str, List[str]] = {
        "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
        "Deepseek": ["deepseek-chat", "deepseek-coder"],
        "OpenAI Compatible": ["custom-model"],
        "Claude": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "Google Gemini": ["gemini-pro", "gemini-1.5-pro"]
    }
    DEFAULT_MODEL = "gpt-4o-mini"
    IMPLETMENTED_AI_PROVIDERS = ["OpenAI", "OpenAI Compatible"]
    # Default endpoints for API providers
    DEFAULT_ENDPOINTS = {
        "OpenAI": "https://api.openai.com/v1",
        "Deepseek": "https://api.deepseek.com/v1",
        "OpenAI Compatible": "",  # User will provide
        "Claude": "https://api.anthropic.com/v1",
        "Google Gemini": "https://generativelanguage.googleapis.com/v1beta"
    }
    
    # Environment variable names for API keys
    ENV_API_KEYS = {
        "OpenAI": "OPENAI_API_KEY",
        "Deepseek": "DEEPSEEK_API_KEY",
        "Claude": "ANTHROPIC_API_KEY",
        "Google Gemini": "GOOGLE_API_KEY"
    }
    
    # Database Settings
    SUPPORTED_DB_TYPES: List[str] = ["SQLite", "MySQL", "PostgreSQL", "SQL Server"]
    DEFAULT_PORTS: Dict[str, str] = {
        "PostgreSQL": "5432",
        "MySQL": "3306",
        "SQL Server": "1433"
    }
    DEFAULT_SQLITE_PATH: str = "assets/adidas_webstore_shoe.db"
    DEFAULT_HOST: str = "localhost"
    
    DEFAULT_MYSQL_HOST: str = os.environ.get("MYSQL_HOST", "")
    DEFAULT_MYSQL_PORT: str = os.environ.get("MYSQL_PORT", "")
    DEFAULT_MYSQL_DATABASE: str = os.environ.get("MYSQL_DATABASE", "")
    DEFAULT_MYSQL_USERNAME: str = os.environ.get("MYSQL_USER", "")
    DEFAULT_MYSQL_PASSWORD: str = os.environ.get("MYSQL_PASSWORD", "")

    # File Export Settings
    EXPORT_FORMATS: List[str] = ["csv", "json", "xlsx"]
    TIMESTAMP_FORMAT: str = "%y%m%d%H%M"
    
    # Table Preview Settings
    DEFAULT_PREVIEW_ROWS: int = 5
    
    # Relationship Analysis Settings
    MIN_CONFIDENCE_SCORE: float = 0.5
    
    @classmethod
    def get_db_port(cls, db_type: str) -> str:
        return cls.DEFAULT_PORTS.get(db_type, "")

    def get_models_for_provider(self, provider: str) -> List[str]:
        """Get available models for a specific provider"""
        return self.AI_MODELS.get(provider, []) 