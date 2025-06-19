import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Dict
import logging
from datetime import datetime
import json
import asyncio
from models.models import Item, SynthesizedArticle
from utils.ai_client import AIClient
from utils.semantic_analyzer import SemanticAnalyzer
from prompts import SYNTHESIZE_PROMPT
from config import Config

class SynthesisService:
    def __init__(self, llm: AIClient, analyzer: SemanticAnalyzer):
        self.llm = llm
        self.analyzer = analyzer

    async def synthesize_article_group(self, group: List[Item]) -> SynthesizedArticle:
        """Synthesize a group of related articles into a single analysis article."""
        if len(group) < 2:
            return None

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
            relationships=relationships_text,
            language=Config.LANGUAGE
        )
        
        article_text = await self.llm.get_completion(prompt)
        
        return SynthesizedArticle(
            tag=main_tag,
            article=article_text,
            date=datetime.now()
        )

    async def process_items(self, items: List[Item]) -> List[SynthesizedArticle]:
        """Process a list of items and generate synthesis articles for related groups."""
        try:
            # Group related articles using semantic analysis
            article_groups = self.analyzer.group_related_articles(items)
            
            # Process each group
            synthesized_articles = []
            for group in article_groups:
                article = await self.synthesize_article_group(group)
                if article:
                    synthesized_articles.append(article)
            
            logging.info(f"Synthesized {len(synthesized_articles)} article groups")
            return synthesized_articles
            
        except Exception as e:
            logging.error(f"Synthesis processing failed: {e}")
            raise 