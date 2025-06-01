import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from models.database import Database
from models.models import State
from config import Config
import logging

def check_novelty(state: State, db: Database) -> State:
    try:
        recent_items = db.get_recent_items(days=Config.NOVELTY_DAYS)
        if not recent_items:
            for item in state.items:
                if item.embedding is not None:
                    item.is_novel = True
            logging.info("No recent items found, marked all as novel")
            return state

        # Convert embeddings to numpy arrays, filtering out None values
        recent_embeddings = [np.array(item.embedding) for item in recent_items if item.embedding is not None]
        if not recent_embeddings:
            for item in state.items:
                if item.embedding is not None:
                    item.is_novel = True
            logging.info("No valid embeddings found in recent items, marked all as novel")
            return state
            
        recent_embeddings = np.vstack(recent_embeddings)

        for item in state.items:
            if item.embedding is not None:
                item_emb = np.array(item.embedding).reshape(1, -1)
                similarities = cosine_similarity(item_emb, recent_embeddings)
                max_sim = similarities.max()
                item.is_novel = max_sim < Config.NOVELTY_THRESHOLD
            else:
                item.is_novel = False
        logging.info("Novelty check completed")
        return state
    except Exception as e:
        logging.error(f"Novelty check failed: {e}")
        raise