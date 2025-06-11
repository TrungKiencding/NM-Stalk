from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    # Azure OpenAI Settings
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    # Voyage AI Settings
    VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
    VOYAGE_MODEL = os.getenv("VOYAGE_MODEL", "voyage-large-2")

    # Database Settings
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "netmind_stalk")
    
    # Database URL
    @classmethod
    def get_database_url(cls):
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    # Application Settings
    NOVELTY_DAYS = 7
    NOVELTY_THRESHOLD = 0.5
    SYNTHESIZE_INTERVAL = 10