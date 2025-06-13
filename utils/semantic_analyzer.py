import numpy as np
from typing import List, Dict, Tuple
from models.models import Item
from sklearn.metrics.pairwise import cosine_similarity
import logging

class SemanticAnalyzer:
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold

    def group_related_articles(self, items: List[Item]) -> List[List[Item]]:
        """
        Group articles based on semantic similarity of their titles and content.
        Returns a list of article groups, where each group contains related articles.
        """
        if not items:
            return []

        # Create embeddings matrix
        embeddings = np.array([item.embedding for item in items if item.embedding is not None])
        if len(embeddings) == 0:
            return [[item] for item in items]

        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(embeddings)

        # Group articles based on similarity
        groups = []
        used_indices = set()

        for i in range(len(items)):
            if i in used_indices:
                continue

            # Find related articles
            related_indices = [j for j in range(len(items)) 
                             if similarity_matrix[i][j] >= self.similarity_threshold]
            
            # Add to group
            group = [items[j] for j in related_indices]
            groups.append(group)
            
            # Mark as used
            used_indices.update(related_indices)

        return groups

    def analyze_article_relationships(self, group: List[Item]) -> Dict[str, List[str]]:
        """
        Analyze relationships between articles in a group.
        Returns a dictionary of relationship types and their descriptions.
        """
        relationships = {
            "common_topics": [],
            "methodological_connections": [],
            "temporal_connections": [],
            "domain_specific": []
        }

        # Extract common topics from content tags
        all_tags = [tag for item in group for tag in (item.content_tags or [])]
        common_tags = set(tag for tag in all_tags if all_tags.count(tag) > 1)
        relationships["common_topics"] = list(common_tags)

        # Analyze titles for methodological connections
        titles = [item.title for item in group if item.title]
        for i, title1 in enumerate(titles):
            for title2 in titles[i+1:]:
                # Look for methodological keywords
                method_keywords = ["method", "approach", "technique", "algorithm", "model", "framework"]
                if any(keyword in title1.lower() and keyword in title2.lower() 
                      for keyword in method_keywords):
                    relationships["methodological_connections"].append(f"{title1} ↔ {title2}")

        # Add temporal analysis if publication dates are available
        dates = [(item.publication_date, item.title) 
                for item in group if item.publication_date and item.title]
        if dates:
            dates.sort(key=lambda x: x[0])
            relationships["temporal_connections"] = [
                f"{title} ({date.strftime('%Y-%m-%d')})" 
                for date, title in dates
            ]

        return relationships 