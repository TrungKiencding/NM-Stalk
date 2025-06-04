from dotenv import load_dotenv
import os
import logging
from typing import Dict

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    # Azure OpenAI Settings
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.5")

    # Voyage AI Settings
    VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
    VOYAGE_MODEL = os.getenv("VOYAGE_MODEL", "voyage-large-2")

    # Application Settings
    DB_PATH = "db.sqlite"
    NOVELTY_DAYS = 7
    NOVELTY_THRESHOLD = 0.5
    SYNTHESIZE_INTERVAL = 10

# Azure OpenAI Config Dict (for compatibility)
AZURE_OPENAI_CONFIG = {
    "URL": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
    "API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
}

def get_azure_config() -> Dict[str, str]:
    """Get Azure OpenAI configuration"""
    if not all(AZURE_OPENAI_CONFIG.values()):
        raise ValueError("Missing Azure OpenAI configuration. Please check your .env file.")
    return AZURE_OPENAI_CONFIG