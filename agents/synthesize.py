import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_client import AIClient
from models.database import Database
from models.models import State, SynthesizedArticle, Item, DBItem
from prompts import SYNTHESIZE_PROMPT
from collections import defaultdict
from config import Config
import logging
from datetime import datetime
import asyncio

def synthesize_articles(state: State, db: Database, llm: AIClient) -> State:
    try:
        if state.session_count % Config.SYNTHESIZE_INTERVAL != 0:
            logging.info("Not synthesizing: not a multiple of interval")
            return state

        # Get all final items from database
        all_final_items = db.session.query(DBItem).filter_by(is_final_selection=True).all()
        all_final_items = [item.to_item() for item in all_final_items]

        tag_to_items = defaultdict(list)
        for item in all_final_items:
            if item.content_tags:  # Check if content_tags exists
                for tag in item.content_tags:
                    tag_to_items[tag].append(item)

        significant_tags = {tag: items for tag, items in tag_to_items.items() if len(items) > 3}

        for tag, items in significant_tags.items():
            unique_items = list(set(items))[:5]
            content = "\n".join([f"{item.title}: {item.summary}" for item in unique_items])
            prompt = SYNTHESIZE_PROMPT.format(tag=tag, content=content)
            article_text = asyncio.run(llm.get_completion(prompt))
            
            synthesized_article = SynthesizedArticle(
                tag=tag,
                article=article_text,
                date=datetime.now()
            )
            db.save_article(synthesized_article)
            state.synthesized_articles.append(synthesized_article)
            
        logging.info(f"Synthesized {len(significant_tags)} articles")
        return state
    except Exception as e:
        logging.error(f"Synthesis failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    state = State()
    db = Database()
    llm = AIClient()
    state = synthesize_articles(state, db, llm)
    print(state)