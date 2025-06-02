import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import Database
from models.models import DBItem
import logging

def print_news_snippets(db_path="db.sqlite"):
    """Display all news snippets from the database."""
    try:
        db = Database(db_path)
        items = db.session.query(DBItem).all()
        
        if not items:
            print("\nNo items found in database.")
            return
            
        print("\n=== News Snippets from Database ===\n")
        for idx, item in enumerate(items, 1):
            print(f"Item #{idx}")
            print(f"Title: {item.title}")
            print(f"URL: {item.url}")
            if item.news_snippet:
                print(f"News Snippet: {item.news_snippet}")
            else:
                print("No news snippet available")
            print(f"Publication Date: {item.publication_date}")
            print("-" * 80 + "\n")
            
    except Exception as e:
        logging.error(f"Failed to print news snippets: {e}")
        raise
    finally:
        if 'db' in locals():
            db.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print_news_snippets() 