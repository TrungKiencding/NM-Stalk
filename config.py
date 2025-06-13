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
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    LANGUAGE = "Vietnamese"
    
    # Database URL
    @classmethod
    def get_database_url(cls):
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    NOVELTY_DAYS = 7

    # ArXiv Settings
    ARXIV_SUBJECT = "cs.AI"
    ARXIV_MAX_RESULTS = 5
    
    # Github Settings
    GITHUB_MAX_REPOS = 5

    # Facebook Settings
    FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL")
    FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD")
    FACEBOOK_PAGES = os.getenv("FACEBOOK_PAGES", "").split(",") if os.getenv("FACEBOOK_PAGES") else []
    MAX_FACEBOOK_POSTS = 4
    
    # Tagging Settings
    ai_tags = [
        "artificial-intelligence",
        "machine-learning",
        "deep-learning",
        "neural-networks",
        "large-language-models",
        "llm",
        "transformers",
        "gpt",
        "bert",
        "chatgpt",
        "gemini",
        "claude",
        "openai",
        "anthropic",
        "google-deepmind",
        "stable-diffusion",
        "midjourney",
        "dalle",
        "multimodal-ai",
        "computer-vision",
        "natural-language-processing",
        "nlp",
        "speech-recognition",
        "text-to-speech",
        "voice-cloning",
        "reinforcement-learning",
        "self-supervised-learning",
        "unsupervised-learning",
        "supervised-learning",
        "few-shot-learning",
        "zero-shot-learning",
        "transfer-learning",
        "federated-learning",
        "edge-ai",
        "quantum-ai",
        "quantum-machine-learning",
        "rag",
        "retrieval-augmented-generation",
        "vector-database",
        "embedding",
        "vector-search",
        "semantic-search",
        "prompt-engineering",
        "fine-tuning",
        "model-compression",
        "model-distillation",
        "model-quantization",
        "explainable-ai",
        "xai",
        "ai-safety",
        "ai-ethics",
        "bias-mitigation",
        "data-augmentation",
        "data-labeling",
        "synthetic-data",
        "generative-ai",
        "diffusion-models",
        "image-generation",
        "video-generation",
        "audio-generation",
        "text-generation",
        "summarization",
        "translation",
        "multilingual-ai",
        "domain-adaptation",
        "knowledge-graphs",
        "graph-neural-networks",
        "gnn",
        "conversational-ai",
        "chatbot",
        "virtual-assistant",
        "autonomous-agents",
        "robotics",
        "computer-aided-diagnosis",
        "medical-ai",
        "ai-in-healthcare",
        "ai-in-finance",
        "ai-in-education",
        "ai-in-robotics",
        "ai-in-vision",
        "ai-in-speech",
        "ai-in-nlp",
        "ai-in-security",
        "ai-in-iot",
        "edge-computing",
        "cloud-ai",
        "distributed-ai",
        "api",
        "huggingface",
        "pytorch",
        "tensorflow",
        "jax",
        "onnx",
        "model-serving",
        "inference",
        "training",
        "dataset",
        "benchmark",
        "open-source-ai",
        "ai-research",
        "ai-trends",
        "ai-tools",
        "ai-architecture",
        "ai-framework"
    ]
