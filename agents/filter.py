import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import State, DBPost
from models.database import Database
import logging
from datetime import datetime, timedelta



def filter_duplicates_posts(state: State, db: Database) -> State:
    """Filter out duplicate posts"""
    try:
        count = 0
        posts_db = db.session.query(DBPost).filter(DBPost.publication_date >= datetime.now().date() - timedelta(days=5)).all()
        for post in state.posts:
            for post_db in posts_db:
                if post.cleaned_text == post_db.cleaned_text:
                    state.posts.remove(post)
                    count += 1
        logging.info(f"Filtered out {count} duplicate posts")
        old_posts = db.session.query(DBPost).filter(DBPost.publication_date < datetime.now().date() - timedelta(days=5)).all()
        db.remove_posts(old_posts)
        for post in state.posts:
            db.save_post(post)
        return state
    except Exception as e:
        logging.error(f"Error filtering duplicate posts: {e}")

def filter_incomplete_items(state: State) -> State:
    """Filter out items that are missing required fields (title, news_snippet, or URL)"""
    try:
        original_count = len(state.items)
        state.items = [
            item for item in state.items 
            if item.title and item.news_snippet and item.url
        ]
        removed_count = original_count - len(state.items)
        if removed_count > 0:
            logging.info(f"Removed {removed_count} items missing required fields")
        return state
    except Exception as e:
        logging.error(f"Error filtering incomplete items: {e}")
        raise

def filter_trash(state: State) -> State:
    """Remove items with tag, title, or news_snippet as 'trash', and synthesized_articles with article as 'No analysis'."""
    try:
        # Filter items
        filtered_items = []
        for item in state.items:
            is_trash = False
            if item.news_snippet and item.news_snippet.strip().lower() == 'trash':
                is_trash = True
            if not is_trash:
                filtered_items.append(item)
        state.items = filtered_items

        return state
    except Exception as e:
        logging.error(f"Error filtering trash items: {e}")
        raise

def filter_output(state: State) -> State:
    try:
        # Initialize database connection
        db = Database()
        
        try:
            logging.info("Filtering data")
            # First filter out incomplete items
            state = filter_incomplete_items(state)
         
            # Then filter out trash items
            state = filter_trash(state)
            
            # Then filter out duplicate posts
            state = filter_duplicates_posts(state, db)
            logging.info("Data filtered")
            return state
        finally:
            db.session.close()
    except Exception as e:
        logging.error(f"Output presentation failed: {e}")
        raise

if __name__ == "__main__":
    state = State()
    state = filter_output(state)
    print(state)