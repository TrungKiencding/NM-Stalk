import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
from models.models import Base, Item, Post, DBItem, DBPost, HotTopic, DBHotTopic
from config import Config



class Database:
    def __init__(self):
        try:
            # Create PostgreSQL database engine
            self.engine = create_engine(Config.get_database_url())
            Base.metadata.create_all(self.engine)
            
            # Create session factory
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            
            logging.info(f"Database initialized at {Config.DB_HOST}:{Config.DB_PORT}")
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            raise

    def save_items(self, items: List[Item]):
        try:
            for item in items:
                db_item = DBItem.from_item(item)
                self.session.merge(db_item)
            self.session.commit()
            logging.info(f"Saved {len(items)} items to database")
            
        except Exception as e:
            self.session.rollback()
            logging.error(f"Failed to save items: {e}")
            raise

    def save_post(self, post: Post):
        try:
            db_post = DBPost.from_post(post)
            self.session.add(db_post)
            self.session.commit()
            logging.info(f"Saved post for source {post.source}")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Failed to save post: {e}")
            raise

    def save_hot_topics(self, hot_topics: List[HotTopic]):
        try:
            for hot_topic in hot_topics:
                db_hot_topic = DBHotTopic.from_hot_topic(hot_topic)
                self.session.merge(db_hot_topic)
            self.session.commit()
            logging.info(f"Saved {len(hot_topics)} hot topics to database")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Failed to save hot topics: {e}")
            raise

    def get_recent_items(self, days=7) -> List[Item]:
        try:
            cutoff = datetime.now() - timedelta(days=days)
            db_items = self.session.query(DBItem).filter(DBItem.timestamp > cutoff).all()
            items = [item.to_item() for item in db_items]
            logging.info(f"Retrieved {len(items)} recent items")
            return items
        except Exception as e:
            logging.error(f"Failed to retrieve recent items: {e}")
            raise

    def get_all_posts(self, days=30) -> List[Post]:
        try:
            cutoff = datetime.now() - timedelta(days=days)
            db_posts = self.session.query(DBPost).filter(DBPost.publication_date >= cutoff).all()
            posts = [post.to_post() for post in db_posts]
            logging.info(f"Retrieved {len(posts)} posts from database")
            return posts
        except Exception as e:
            logging.error(f"Failed to retrieve posts: {e}")
            raise

    def remove_posts(self, posts: List[DBPost]):
        try:
            for post in posts:
                self.session.delete(post)
            self.session.commit()
            logging.info(f"Removed {len(posts)} posts from database")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Failed to remove posts: {e}")
            raise

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'session'):
            self.session.close()
