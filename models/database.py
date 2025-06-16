import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
import uuid
from models.models import Base, Item, SynthesizedArticle, DBItem, DBArticle
from config import Config
from utils.ai_client import AIClient
from utils.semantic_analyzer import SemanticAnalyzer
from services.synthesis_service import SynthesisService
from models.models import State
import json
import asyncio
from prompts import SYNTHESIZE_PROMPT

class Database:
    def __init__(self):
        try:
            # Create PostgreSQL database engine
            self.engine = create_engine(Config.get_database_url())
            Base.metadata.create_all(self.engine)
            
            # Create session factory
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            # Initialize AI client and semantic analyzer
            self.llm = AIClient()
            self.analyzer = SemanticAnalyzer(similarity_threshold=0.7)
            
            # Initialize synthesis service
            self.synthesis_service = SynthesisService(self.llm, self.analyzer)
            
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
            
            # Trigger synthesis after saving items
            self._trigger_synthesis()
        except Exception as e:
            self.session.rollback()
            logging.error(f"Failed to save items: {e}")
            raise

    def save_article(self, article: SynthesizedArticle):
        try:
            db_article = DBArticle.from_article(article)
            self.session.add(db_article)
            self.session.commit()
            logging.info(f"Saved article for tag {article.tag}")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Failed to save article: {e}")
            raise

    def _trigger_synthesis(self):
        """Trigger synthesis of articles after database update"""
        try:
            # Get all final items from database
            all_final_items = self.session.query(DBItem).all()
            all_final_items = [item.to_item() for item in all_final_items]

            # Group related articles using semantic analysis
            article_groups = self.analyzer.group_related_articles(all_final_items)

            # Process each group of related articles
            for group in article_groups:
                if len(group) < 2:  # Skip groups with only one article
                    continue

                # Get the most common tag as the group's topic
                tag_counts = {}
                for item in group:
                    if item.content_tags:
                        for tag in item.content_tags:
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1
                main_tag = max(tag_counts.items(), key=lambda x: x[1])[0] if tag_counts else "general"

                # Analyze relationships between articles in the group
                relationships = self.analyzer.analyze_article_relationships(group)

                # Prepare content for synthesis
                content = "\n\n".join([
                    f"Title: {item.title}\n"
                    f"Summary: {item.summary}\n"
                    f"Tags: {', '.join(item.content_tags or [])}\n"
                    f"Source: {item.source}"
                    for item in group
                ])

                # Format relationships for the prompt
                relationships_text = json.dumps(relationships, indent=2)

                # Generate synthesis article
                prompt = SYNTHESIZE_PROMPT.format(
                    tag=main_tag,
                    content=content,
                    relationships=relationships_text
                )
                
                article_text = asyncio.run(self.llm.get_completion(prompt))
                
                synthesized_article = SynthesizedArticle(
                    tag=main_tag,
                    article=article_text,
                    date=datetime.now()
                )
                self.save_article(synthesized_article)
                
            logging.info(f"Synthesized {len(article_groups)} article groups")
        except Exception as e:
            logging.error(f"Synthesis failed: {e}")
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

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'session'):
            self.session.close()
