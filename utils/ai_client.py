import httpx
from openai import AsyncAzureOpenAI
from config import Config
import logging
from typing import List, Union
import json
import base64
import numpy as np

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
                http_client=httpx.AsyncClient(verify=False)
            )
        except Exception as e:
            logging.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise

    def _base64_to_float_array(self, base64_str: str) -> List[float]:
        """Convert base64 string to float array"""
        decoded_bytes = base64.b64decode(base64_str)
        return list(np.frombuffer(decoded_bytes, dtype=np.float32))

    async def get_embedding(self, text: Union[str, List[str]], model: str = "voyage-3-large") -> List[float]:
        """
        Get embedding using Voyage AI
        :param text: Text to embed (string or list of strings)
        :param model: Voyage model to use (default: voyage-large-3)
        :return: List of embeddings
        """
        try:
            # Prepare the input
            if isinstance(text, str):
                input_texts = [text]
            else:
                input_texts = text

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.voyage_base_url}/embeddings",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.voyage_api_key}"
                    },
                    json={
                        "model": model,
                        "input": input_texts,
                        "encoding_format": "base64"
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Voyage API error: {response.text}")
                
                result = response.json()
                # Convert base64 embeddings to float arrays
                embeddings = [self._base64_to_float_array(data["embedding"]) for data in result["data"]]
                
                # Return single embedding for single input, list for multiple
                return embeddings[0] if isinstance(text, str) else embeddings
                
        except Exception as e:
            logging.error(f"Error getting Voyage embedding: {e}")
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
