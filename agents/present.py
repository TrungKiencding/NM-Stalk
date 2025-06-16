import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import State
from models.database import Database
from config import Config
import logging
import numpy as np
from typing import List, Dict, Tuple, Set
from sklearn.metrics.pairwise import cosine_similarity

def get_source_priority(source: str) -> int:
    """Return priority score for each source (lower is higher priority)"""
    priorities = {
        "GitHub": 0,
        "arXiv": 1,
        "Facebook": 2
    }
    return priorities.get(source, 999)  # Unknown sources get lowest priority

def find_similar_articles(items: List[Dict], threshold: float = 0.85) -> List[Tuple[int, int, float]]:
    """Find pairs of similar articles based on their embeddings"""
    similar_pairs = []
    
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i].embedding is None or items[j].embedding is None:
                continue
                
            # Convert embeddings to numpy arrays
            emb1 = np.array(items[i].embedding).reshape(1, -1)
            emb2 = np.array(items[j].embedding).reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(emb1, emb2)[0][0]
            
            if similarity > threshold:
                similar_pairs.append((i, j, similarity))
                
    return similar_pairs

def check_db_duplicates(state: State, db: Database, threshold: float = 0.85) -> Set[int]:
    """Check for duplicates between current items and database items"""
    try:
        # Get recent items from database
        db_items = db.get_recent_items(days=Config.NOVELTY_DAYS)
        to_remove = set()
        
        # For each current item
        for idx, current_item in enumerate(state.items):
            if current_item.embedding is None:
                continue
                
            current_emb = np.array(current_item.embedding).reshape(1, -1)
            current_priority = get_source_priority(current_item.source)
            
            # Compare with database items
            for db_item in db_items:
                if db_item.embedding is None:
                    continue
                    
                db_emb = np.array(db_item.embedding).reshape(1, -1)
                similarity = cosine_similarity(current_emb, db_emb)[0][0]
                
                if similarity > threshold:
                    db_priority = get_source_priority(db_item.source)
                    # If current item has lower or equal priority, mark it for removal
                    if current_priority >= db_priority:
                        to_remove.add(idx)
                        break
                        
        if to_remove:
            logging.info(f"Found {len(to_remove)} items that are similar to existing database entries")
            
        return to_remove
    except Exception as e:
        logging.error(f"Error checking database duplicates: {e}")
        raise

def filter_duplicates(state: State, db: Database) -> State:
    """Filter out duplicate articles based on embedding similarity and source priority"""
    try:
        # First check for duplicates within current items
        similar_pairs = find_similar_articles(state.items)
        to_remove = set()
        
        # For each pair of similar articles
        for i, j, similarity in similar_pairs:
            # Get source priorities
            priority_i = get_source_priority(state.items[i].source)
            priority_j = get_source_priority(state.items[j].source)
            
            # Remove the one with lower priority (higher priority number)
            if priority_i > priority_j:
                to_remove.add(i)
            else:
                to_remove.add(j)
        
        # Then check for duplicates in database
        db_duplicates = check_db_duplicates(state, db)
        to_remove.update(db_duplicates)
        
        # Create new list without duplicates
        state.items = [item for idx, item in enumerate(state.items) if idx not in to_remove]
        
        if to_remove:
            logging.info(f"Removed {len(to_remove)} duplicate articles in total")
            
        return state
    except Exception as e:
        logging.error(f"Error filtering duplicates: {e}")
        raise

def present_output(state: State) -> State:
    try:
        # Initialize database connection
        db = Database()
        
        try:
            # First filter out duplicates
            state = filter_duplicates(state, db)
            
            # Then present the remaining items
            for item in state.items:
                print("\nFinal selections:")
                if item.news_snippet:
                    print(f"[{item.source}] {item.news_snippet}")
                    
            for article in state.synthesized_articles:
                print("\nSynthesized articles:")
                print(f"Article on {article.tag}:\n{article.article}\n")
                
            logging.info("Output presented")
            return state
        finally:
            db.session.close()
    except Exception as e:
        logging.error(f"Output presentation failed: {e}")
        raise

if __name__ == "__main__":
    state = State()
    state = present_output(state)
    print(state)