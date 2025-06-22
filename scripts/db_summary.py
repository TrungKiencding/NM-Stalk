import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import Database
from models.models import DBItem, DBPost, DBHotTopic
import logging
from datetime import datetime

def print_database_summary():
    """Display comprehensive information about all items in the database."""
    try:
        db = Database()
        items = db.session.query(DBItem).order_by(DBItem.timestamp.desc()).all()
        posts = db.session.query(DBPost).order_by(DBPost.publication_date.desc()).all()
        hot_topics = db.session.query(DBHotTopic).order_by(DBHotTopic.publication_date.desc()).all()
        
        if not items and not hot_topics:
            print("\nDatabase is empty.")
            return
            
        # Print Items Summary
        print("\n" + "="*100)
        print("DATABASE SUMMARY".center(100))
        print("="*100)
        
        # Print total counts
        print(f"\nTotal Items: {len(items)}")
        print(f"Total Posts: {len(posts)}")
        print(f"Total Hot Topics: {len(hot_topics)}")
        
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
            elif item.content_snippet:
                print("\nContent Snippet:")
                print("-" * 80)
                print(item.content_snippet)
                print("-" * 80)
                
            if item.summary:
                print("\nSummary:")
                print("-" * 80)
                print(item.summary)
                print("-" * 80)
                
            print("\n" + "-"*100 + "\n")
        # Print Hot Topics
        if hot_topics:
            print("\n" + "="*100)
            print("HOT TOPICS".center(100))
            print("="*100 + "\n")
            
            for idx, topic in enumerate(hot_topics, 1):
                print(f"Hot Topic #{idx}")
                print(f"ID: {topic.id}")
                print(f"Publication Date: {topic.publication_date}")
                
                if topic.snippet:
                    print("\nSnippet:")
                    print("-" * 80)
                    print(topic.snippet)
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