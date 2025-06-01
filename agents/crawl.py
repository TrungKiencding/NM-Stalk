import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import State, Item
from datetime import datetime
import logging
import json
import uuid

def simulate_crawl() -> list[Item]:
    try:
        with open('crawl_data/collected_post_test.json', 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
        
        items = []
        for raw_item in raw_data:
            # Create a new Item with required fields
            item = Item(
                id=str(uuid.uuid4()),  # Generate a unique ID
                url=raw_item["link"],  # Map link to url
                title=raw_item["link"],
                content_snippet=raw_item["raw_content"],
                publication_date=datetime.now(),  # Current time as we don't have original date
                source="GitHub",
                timestamp=datetime.now()
            )
            items.append(item)
        logging.info(f"Simulated crawl for Github: {len(items)} items")
        return items
    except Exception as e:
        logging.error(f"Failed to simulate crawl for Github: {e}")
        raise
def crawl_data(state: State) -> State:
    try:
        github_items = simulate_crawl()
        state.items.extend(github_items)
        logging.info(f"Crawled {len(github_items)} items")
        return state
    except Exception as e:
        logging.error(f"Crawl data failed: {e}")
        raise
