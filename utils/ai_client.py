import httpx
from openai import AsyncAzureOpenAI
from config import Config
import logging
from typing import List, Union
import numpy as np
import requests

class AIClient:
    def __init__(self):
        self.config = Config
        self.azure_client = self._initialize_azure_client()
        self.voyage_api_key = self.config.VOYAGE_API_KEY
        self.voyage_base_url = "https://api.voyageai.com/v1"

    def _initialize_azure_client(self):
        """Initialize Azure OpenAI client"""
        try:
            return AsyncAzureOpenAI(
                azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT,
                api_key=self.config.AZURE_OPENAI_API_KEY,
                api_version=self.config.AZURE_OPENAI_API_VERSION,
                http_client=httpx.AsyncClient()
            )
        except Exception as e:
            logging.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise

    @staticmethod
    def get_embedding_model():
        """Get Voyage embedding model for BERTopic"""
        try:
            # Return a VoyageEmbeddingModel class that implements the required interface
            return VoyageEmbeddingModel()
        except Exception as e:
            logging.error(f"Failed to load Voyage embedding model: {e}")
            raise

    async def get_completion(self, prompt: str, model: str = None) -> str:
        """
        Get completion from Azure OpenAI
        :param prompt: The prompt text
        :param model: Optional model override (defaults to config)
        :return: Completion text
        """
        try:
            model = model or self.config.AZURE_OPENAI_DEPLOYMENT_NAME
            response = await self.azure_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error getting completion: {e}")
            raise

    async def get_embedding(self, texts: List[str], model: str = "voyage-3-large") -> List[List[float]]:
        """
        Get embeddings from Voyage AI
        :param texts: List of texts to embed
        :param model: Voyage model name
        :return: List of embedding vectors
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.voyage_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "input": texts,
                "model": model
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.voyage_base_url}/embeddings",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return [embedding["embedding"] for embedding in result["data"]]
                
        except Exception as e:
            logging.error(f"Error getting embeddings from Voyage AI: {e}")
            raise

    def get_embedding_sync(self, texts: List[str], model: str = "voyage-3-large") -> List[List[float]]:
        """
        Get embeddings from Voyage AI synchronously
        :param texts: List of texts to embed
        :param model: Voyage model name
        :return: List of embedding vectors
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.voyage_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "input": texts,
                "model": model
            }
            
            response = requests.post(
                f"{self.voyage_base_url}/embeddings",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return [embedding["embedding"] for embedding in result["data"]]
                
        except Exception as e:
            logging.error(f"Error getting embeddings from Voyage AI: {e}")
            raise


class VoyageEmbeddingModel:
    """Wrapper class to make Voyage embeddings compatible with BERTopic"""
    
    def __init__(self):
        # Avoid circular import by accessing config directly
        self.voyage_api_key = Config.VOYAGE_API_KEY
        self.voyage_base_url = "https://api.voyageai.com/v1"
        self.model_name = "voyage-3-large"
    
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """
        Encode texts to embeddings using Voyage AI
        This method is called by BERTopic and needs to be synchronous
        """
        try:
            # Convert to list if single string
            if isinstance(texts, str):
                texts = [texts]
            
            # Always use synchronous approach for BERTopic compatibility
            return self._encode_sync(texts)
                
        except Exception as e:
            logging.error(f"Error in Voyage embedding encode: {e}")
            raise

    def _encode_sync(self, texts: List[str]) -> np.ndarray:
        """Synchronous encoding using requests"""
        try:
            headers = {
                "Authorization": f"Bearer {self.voyage_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "input": texts,
                "model": self.model_name
            }
            
            response = requests.post(
                f"{self.voyage_base_url}/embeddings",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            embeddings = [embedding["embedding"] for embedding in result["data"]]
            
            return np.array(embeddings)
            
        except Exception as e:
            logging.error(f"Error in synchronous Voyage embedding: {e}")
            raise 