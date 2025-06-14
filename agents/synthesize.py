import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_client import AIClient
from models.database import Database
from models.models import State, SynthesizedArticle, Item, DBItem
from services.synthesis_service import SynthesisService
import logging
import asyncio

def synthesize_articles(state: State, db: Database, llm: AIClient) -> State:
    """
    This function is now a wrapper that triggers synthesis through the database.
    The actual synthesis logic has been moved to SynthesisService.
    """
    try:
        # Get all final items from database
        all_final_items = db.session.query(DBItem).all()
        all_final_items = [item.to_item() for item in all_final_items]

        # Process items using synthesis service
        synthesized_articles = asyncio.run(
            db.synthesis_service.process_items(all_final_items)
        )

        # Update state with synthesized articles
        state.synthesized_articles.extend(synthesized_articles)
        
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