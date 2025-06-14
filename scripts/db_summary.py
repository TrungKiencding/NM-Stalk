import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import Database
from models.models import DBItem, DBArticle
import logging
from datetime import datetime

def print_database_summary():
    """Display comprehensive information about all items in the database."""
    try:
        db = Database()
        items = db.session.query(DBItem).order_by(DBItem.timestamp.desc()).all()
        articles = db.session.query(DBArticle).order_by(DBArticle.date.desc()).all()
        
        if not items and not articles:
            print("\nDatabase is empty.")
            return
            
        # Print Items Summary
        print("\n" + "="*100)
        print("DATABASE SUMMARY".center(100))
        print("="*100)
        
        # Print total counts
        print(f"\nTotal Items: {len(items)}")
        print(f"Total Synthesized Articles: {len(articles)}")
        
        # Print Items
        if items:
            print("\n" + "="*100)
            print("RESEARCH ITEMS".center(100))
            print("="*100 + "\n")
            
        for idx, item in enumerate(items, 1):
            print(f"Item #{idx}")
                print(f"ID: {item.id}")
            print(f"Title: {item.title}")
                print(f"Source: {item.source}")
            print(f"URL: {item.url}")
                print(f"Publication Date: {item.publication_date}")
                print(f"Last Updated: {item.timestamp}")
                
                if item.content_tags:
                    print("Tags:", ", ".join(item.content_tags))
                
            if item.news_snippet:
                    print("\nNews Snippet:")
                    print("-" * 80)
                    print(item.news_snippet)
                    print("-" * 80)
                
                if item.related_content:
                    print("\nRelated Content:")
                    for content in item.related_content:
                        print(f"- {content.get('link', 'No link available')}")
                
                print("\n" + "-"*100 + "\n")
        
        # Print Synthesized Articles
        if articles:
            print("\n" + "="*100)
            print("SYNTHESIZED ARTICLES".center(100))
            print("="*100 + "\n")
            
            for idx, article in enumerate(articles, 1):
                print(f"Article #{idx}")
                print(f"ID: {article.id}")
                print(f"Tag: {article.tag}")
                print(f"Date: {article.date}")
                print("\nContent:")
                print("-" * 80)
                print(article.article)
                print("-" * 80)
                print("\n" + "-"*100 + "\n")
            
    except Exception as e:
        logging.error(f"Failed to print database summary: {e}")
        raise
    finally:
        if 'db' in locals():
            db.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print_database_summary() 