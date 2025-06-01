import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import Database
from models.models import DBItem, DBArticle, Item, SynthesizedArticle
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging
from typing import Optional
import json
import uuid

def insert_test_data(db: Database):
    try:
        # Create test items
        test_items = [
            Item(
                id=str(uuid.uuid4()),
                url="https://example.com/1",
                title="Test Article 1",
                content_snippet="This is a test article about LLMs",
                publication_date=datetime.now(),
                cleaned_text="This is a test article about LLMs",
                content_tags=["llm", "ai", "machine-learning"],
                source_tags=["test"],
                embedding=[0.1] * 10,  # dummy embedding
                source="test",
                timestamp=datetime.now(),
                is_novel=True,
                summary="A test article about LLMs",
                news_snippet="Breaking: New test article about LLMs",
                is_final_selection=True
            ),
            Item(
                id=str(uuid.uuid4()),
                url="https://example.com/2",
                title="Test Article 2",
                content_snippet="This is a test article about RAG",
                publication_date=datetime.now(),
                cleaned_text="This is a test article about RAG",
                content_tags=["rag", "ai", "machine-learning"],
                source_tags=["test"],
                embedding=[0.2] * 10,  # dummy embedding
                source="test",
                timestamp=datetime.now(),
                is_novel=True,
                summary="A test article about RAG",
                news_snippet="Breaking: New test article about RAG",
                is_final_selection=True
            )
        ]

        # Create test articles
        test_articles = [
            SynthesizedArticle(
                tag="ai",
                article="This is a synthesized article about AI combining multiple sources...",
                date=datetime.now()
            ),
            SynthesizedArticle(
                tag="machine-learning",
                article="This is a synthesized article about machine learning trends...",
                date=datetime.now()
            )
        ]

        # Save to database
        for item in test_items:
            db_item = DBItem.from_item(item)
            db.session.merge(db_item)

        for article in test_articles:
            db_article = DBArticle.from_article(article, str(uuid.uuid4()))
            db.session.add(db_article)

        db.session.commit()
        print("Test data inserted successfully")

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to insert test data: {e}")
        raise

def clean_tags(tags):
    """Convert string representation of tags to actual list if needed"""
    if isinstance(tags, str):
        try:
            return json.loads(tags)
        except:
            return [tags]
    return tags

def print_article_by_tag(db: Database, tag: str):
    try:
        article = db.session.query(DBArticle).filter_by(tag=tag).first()
        if article:
            print(f"\n=== Article: {article.tag} ===")
            print(f"Date: {article.date}")
            print("\nContent:")
            print(article.article)
        else:
            print(f"\nNo article found with tag: {tag}")
    except Exception as e:
        logging.error(f"Failed to print article: {e}")

def print_article_by_id(db: Database, article_id: str):
    try:
        article = db.session.query(DBArticle).filter_by(id=article_id).first()
        if article:
            print(f"\n=== Article ID: {article.id} ===")
            print(f"Tag: {article.tag}")
            print(f"Date: {article.date}")
            print("\nContent:")
            print(article.article)
        else:
            print(f"\nNo article found with ID: {article_id}")
    except Exception as e:
        logging.error(f"Failed to print article: {e}")

def list_available_articles(db: Database):
    try:
        articles = db.session.query(DBArticle).all()
        print("\n=== Available Articles ===")
        for article in articles:
            print(f"ID: {article.id} | Tag: {article.tag} | Date: {article.date}")
    except Exception as e:
        logging.error(f"Failed to list articles: {e}")

def summarize_database(db_path="db.sqlite"):
    try:
        db = Database(db_path)
        
        # Get all items
        items = db.session.query(DBItem).all()
        
        # Get recent items (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_items = db.session.query(DBItem).filter(DBItem.timestamp > week_ago).all()
        
        # Get novel items
        novel_items = db.session.query(DBItem).filter_by(is_novel=True).all()
        
        # Get final selection items
        final_items = db.session.query(DBItem).filter_by(is_final_selection=True).all()
        
        # Get synthesized articles
        articles = db.session.query(DBArticle).all()
        
        # Analyze content tags
        all_tags = []
        for item in items:
            if item.content_tags:
                all_tags.extend(item.content_tags)
        tag_counts = Counter(all_tags)
        
        # Print summary
        print("\n=== Database Summary ===")
        print(f"\nTotal Items: {len(items)}")
        print(f"Items from last 7 days: {len(recent_items)}")
        print(f"Novel Items: {len(novel_items)}")
        print(f"Final Selection Items: {len(final_items)}")
        print(f"Synthesized Articles: {len(articles)}")
        
        print("\nTop 10 Content Tags:")
        for tag, count in tag_counts.most_common(10):
            print(f"  {tag}: {count}")
            
        print("\nRecent Articles:")
        for article in sorted(articles, key=lambda x: x.date, reverse=True)[:5]:
            print(f"\n  Topic: {article.tag}")
            print(f"  Date: {article.date}")
            print(f"  Summary: {article.article[:200]}...")
            
        print("\nRecent Final Selections:")
        for item in sorted(final_items, key=lambda x: x.timestamp or datetime.min, reverse=True)[:5]:
            print(f"\n  Title: {item.title}")
            print(f"  Date: {item.timestamp}")
            if item.news_snippet:
                print(f"  Snippet: {item.news_snippet[:200]}...")
                
    except Exception as e:
        logging.error(f"Failed to summarize database: {e}")
        raise
    finally:
        if 'db' in locals():
            db.session.close()

def print_final_summary(db: Database):
    try:
        # Get all final selection items
        final_items = db.session.query(DBItem).filter_by(is_final_selection=True).all()
        
        # Group items by content tags
        tag_items = defaultdict(list)
        for item in final_items:
            if item.content_tags:
                tags = clean_tags(item.content_tags)
                for tag in tags:
                    tag_items[tag].append(item)
        
        # Get synthesized articles
        articles = db.session.query(DBArticle).order_by(DBArticle.date.desc()).all()
        
        if not final_items and not articles:
            print("\nNo final selections or synthesized articles found.")
            print("You can insert test data using: python db_summary.py test")
            return

        print("\n=== Final Summary Report ===")
        print(f"\nTotal Final Selections: {len(final_items)}")
        print(f"Total Synthesized Articles: {len(articles)}")
        
        print("\n=== Synthesized Articles with Related Items ===")
        for article in articles:
            print(f"\n{'-'*80}")
            print(f"Article Topic: {article.tag}")
            print(f"Date: {article.date}")
            print("\nSynthesized Content:")
            print(article.article)
            
            # Print related final items
            related_items = tag_items.get(article.tag, [])
            if related_items:
                print("\nRelated Final Selections:")
                for item in related_items:
                    print(f"\n- Title: {item.title}")
                    if item.news_snippet:
                        print(f"  Snippet: {item.news_snippet}")
                    print(f"  URL: {item.url}")
            print(f"\n{'-'*80}")
            
    except Exception as e:
        logging.error(f"Failed to print final summary: {e}")

def print_items(db_path="db.sqlite"):
    try:
        db = Database(db_path)
        items = db.session.query(DBItem).all()
        
        if not items:
            print("\nNo items found in database.")
            return
            
        print("\n=== All Items ===\n")
        for item in items:
            print(f"Title: {item.title}")
            if item.news_snippet:
                print(f"Snippet: {item.news_snippet}")
            print("-" * 80 + "\n")
            
    except Exception as e:
        logging.error(f"Failed to print items: {e}")
        raise
    finally:
        if 'db' in locals():
            db.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print_items() 