from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
import uuid
from models.models import Base, Item, SynthesizedArticle, DBItem, DBArticle
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

    def save_article(self, article: SynthesizedArticle):
        try:
            db_article = DBArticle.from_article(article, str(uuid.uuid4()))
            self.session.add(db_article)
            self.session.commit()
            logging.info(f"Saved article for tag {article.tag}")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Failed to save article: {e}")
            raise

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'session'):
            self.session.close()
