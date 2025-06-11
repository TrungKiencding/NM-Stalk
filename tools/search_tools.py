import os
import requests
from typing import Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()

class SearchTools:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.session = requests.Session()

    def google_search(self, query: str, **params) -> Dict[str, Any]:
        """
        Perform a search using the Google Search Engine.
        Args:
            query (str): Search query
            **params: Additional parameters for the search
        Returns:
            dict: JSON response of the search results
        """
        try:
            base_url = 'https://www.googleapis.com/customsearch/v1'
            search_params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                **params
            }
            
            response = self.session.get(base_url, params=search_params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Google search failed: {e}")
            return {} 