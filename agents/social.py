import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import State, DBPost, Post, HotTopic
from models.database import Database
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from bertopic import BERTopic
from utils.ai_client import AIClient
import numpy as np
from collections import Counter
import json
import asyncio
from prompts import SOCIAL_PROMPT
import uuid
from datetime import timezone


class SocialAnalyzer:
    def __init__(self, llm: AIClient):
        """Initialize the Social Analyzer with BERTopic for clustering"""
        self.db = Database()
        self.llm = llm
        self.topic_model = None
        self.embedding_model = AIClient.get_embedding_model()
        self.clusters = None
        self.cluster_analysis = None
        
    def get_all_posts(self, days_back: int = 5) -> List[Post]:
        """Retrieve all posts from the database within the specified time range"""
        try:
            posts = self.db.get_all_posts(days_back)
            logging.info(f"Retrieved {len(posts)} posts from database")
            return posts
        except Exception as e:
            logging.error(f"Error retrieving posts: {e}")
            raise
    
    def preprocess_titles(self, posts: List[Post]) -> Tuple[List[str], List[Post]]:
        """Preprocess post titles for clustering"""
        processed_titles = []
        valid_posts = []
        
        for post in posts:
            if post.title and post.title.strip():
                # Clean the title
                title = post.title.strip()
                # Remove very short titles (likely not meaningful)
                if len(title) > 10:
                    processed_titles.append(title)
                    valid_posts.append(post)
        
        logging.info(f"Preprocessed {len(processed_titles)} valid titles from {len(posts)} posts")
        return processed_titles, valid_posts
    
    def perform_clustering(self, titles: List[str], posts: List[Post]) -> Dict[str, Any]:
        """Perform BERTopic clustering on post titles using Voyage embeddings"""
        try:
            if len(titles) < 5:
                logging.warning("Not enough titles for meaningful clustering (minimum 5 required)")
                return {
                    "clusters": [],
                    "topics": [],
                    "posts_by_cluster": {},
                    "cluster_stats": {},
                    "topics_keywords": {},
                    "total_posts": len(posts),
                    "total_clusters": 0,
                    "outliers": len(posts)
                }
            
            logging.info(f"Starting clustering with {len(titles)} titles")
            
            # Initialize BERTopic with Voyage embedding model
            self.topic_model = BERTopic(
                embedding_model=self.embedding_model,
                min_topic_size=2,
                nr_topics="auto",
                verbose=True
            )
            
            # Fit the model
            logging.info("Fitting BERTopic model...")
            topics, probs = self.topic_model.fit_transform(titles)
            
            logging.info(f"BERTopic fit completed. Topics shape: {len(topics)}, Probs type: {type(probs)}")
            if probs is not None:
                logging.info(f"Probs shape: {getattr(probs, 'shape', 'No shape attribute')}")
            
            # Get topic info
            topic_info = self.topic_model.get_topic_info()
            logging.info(f"Topic info retrieved: {len(topic_info)} topics")
            
            # Organize posts by cluster
            posts_by_cluster = {}
            for i, (title, post, topic) in enumerate(zip(titles, posts, topics)):
                if topic not in posts_by_cluster:
                    posts_by_cluster[topic] = []
                
                # Safely get probability
                probability = 1.0
                if probs is not None:
                    try:
                        # Handle different probs array structures
                        if hasattr(probs, 'shape') and len(probs.shape) == 2:
                            # 2D array: probs[i][topic]
                            if i < probs.shape[0] and topic < probs.shape[1]:
                                probability = float(probs[i][topic])
                        elif hasattr(probs, 'shape') and len(probs.shape) == 1:
                            # 1D array: probs[i]
                            if i < len(probs):
                                probability = float(probs[i])
                        else:
                            # Scalar or other structure
                            probability = float(probs) if isinstance(probs, (int, float)) else 1.0
                    except (IndexError, TypeError, ValueError) as e:
                        logging.warning(f"Error getting probability for item {i}, topic {topic}: {e}")
                        probability = 1.0
                
                posts_by_cluster[topic].append({
                    "post": post,
                    "title": title,
                    "probability": probability
                })
            
            logging.info(f"Organized posts into {len(posts_by_cluster)} clusters")
            
            # Calculate cluster statistics
            cluster_stats = {}
            for topic_id in posts_by_cluster.keys():
                if topic_id != -1:  # Skip outliers
                    cluster_posts = posts_by_cluster[topic_id]
                    
                    # Safely get date range
                    dates = [p["post"].publication_date for p in cluster_posts if p["post"].publication_date]
                    date_range = {}
                    if dates:
                        date_range = {
                            "earliest": min(dates),
                            "latest": max(dates)
                        }
                    else:
                        date_range = {
                            "earliest": None,
                            "latest": None
                        }
                    
                    cluster_stats[topic_id] = {
                        "count": len(cluster_posts),
                        "avg_probability": np.mean([p["probability"] for p in cluster_posts]),
                        "sources": list(set([p["post"].source for p in cluster_posts if p["post"].source])),
                        "date_range": date_range
                    }
            
            # Get topic keywords
            topics_keywords = {}
            for topic_id in posts_by_cluster.keys():
                if topic_id != -1:
                    try:
                        topic_keywords = self.topic_model.get_topic(topic_id)
                        topics_keywords[topic_id] = [word for word, _ in topic_keywords[:10]]
                    except Exception as e:
                        logging.warning(f"Error getting keywords for topic {topic_id}: {e}")
                        topics_keywords[topic_id] = []
            
            self.clusters = {
                "topics": topic_info.to_dict('records'),
                "posts_by_cluster": posts_by_cluster,
                "cluster_stats": cluster_stats,
                "topics_keywords": topics_keywords,
                "total_posts": len(posts),
                "total_clusters": len([t for t in topics if t != -1]),
                "outliers": len([t for t in topics if t == -1])
            }
            
            logging.info(f"Clustering completed: {self.clusters['total_clusters']} clusters, {self.clusters['outliers']} outliers")
            return self.clusters
            
        except Exception as e:
            logging.error(f"Error performing clustering: {e}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            # Return a fallback structure to prevent complete failure
            logging.warning("Returning fallback clustering structure due to error")
            return {
                "clusters": [],
                "topics": [],
                "posts_by_cluster": {},
                "cluster_stats": {},
                "topics_keywords": {},
                "total_posts": len(posts),
                "total_clusters": 0,
                "outliers": len(posts)
            }
    
    def analyze_clusters(self) -> Dict[str, Any]:
        """Analyze the clustering results and generate insights"""
        if not self.clusters:
            logging.warning("No clusters available for analysis")
            return {}
        
        try:
            analysis = {
                "summary": {
                    "total_posts": self.clusters["total_posts"],
                    "total_clusters": self.clusters["total_clusters"],
                    "outliers_percentage": (self.clusters["outliers"] / self.clusters["total_posts"]) * 100,
                    "avg_cluster_size": self.clusters["total_posts"] / max(self.clusters["total_clusters"], 1)
                },
                "top_clusters": [],
                "trending_topics": [],
                "source_analysis": {},
                "recommendations": []
            }
            
            # Find top clusters by size
            cluster_sizes = [(topic_id, stats["count"]) 
                           for topic_id, stats in self.clusters["cluster_stats"].items()]
            cluster_sizes.sort(key=lambda x: x[1], reverse=True)
            
            analysis["top_clusters"] = []
            for topic_id, size in cluster_sizes[:5]:
                cluster_info = {
                    "topic_id": topic_id,
                    "size": size,
                    "keywords": self.clusters["topics_keywords"].get(topic_id, []),
                    "sources": self.clusters["cluster_stats"][topic_id]["sources"],
                    "avg_probability": self.clusters["cluster_stats"][topic_id]["avg_probability"]
                }
                analysis["top_clusters"].append(cluster_info)
            
            # Analyze sources
            all_sources = []
            for stats in self.clusters["cluster_stats"].values():
                all_sources.extend(stats["sources"])
            
            source_counts = Counter(all_sources)
            analysis["source_analysis"] = {
                "top_sources": source_counts.most_common(5),
                "total_unique_sources": len(set(all_sources))
            }
            
            # Generate recommendations
            if analysis["summary"]["outliers_percentage"] > 20:
                analysis["recommendations"].append(
                    "High number of outliers detected. Consider adjusting clustering parameters."
                )
            
            if analysis["summary"]["avg_cluster_size"] < 3:
                analysis["recommendations"].append(
                    "Clusters are very small. Consider reducing min_topic_size parameter."
                )
            
            if len(analysis["top_clusters"]) > 0:
                analysis["recommendations"].append(
                    f"Top trending topic: {analysis['top_clusters'][0]['keywords'][:3]}"
                )
            
            self.cluster_analysis = analysis
            logging.info("Cluster analysis completed")
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing clusters: {e}")
            raise
    
    def get_cluster_posts(self, topic_id: int) -> List[Dict[str, Any]]:
        """Get all posts for a specific cluster"""
        if not self.clusters or topic_id not in self.clusters["posts_by_cluster"]:
            return []
        
        return self.clusters["posts_by_cluster"][topic_id]
    
    def get_trending_topics(self, min_size: int = 3) -> List[Dict[str, Any]]:
        """Get trending topics (clusters with minimum size)"""
        if not self.clusters:
            return []
        
        trending = []
        for topic_id, stats in self.clusters["cluster_stats"].items():
            if stats["count"] >= min_size:
                trending.append({
                    "topic_id": topic_id,
                    "size": stats["count"],
                    "keywords": self.clusters["topics_keywords"].get(topic_id, []),
                    "sources": stats["sources"],
                    "avg_probability": stats["avg_probability"]
                })
        
        # Sort by size
        trending.sort(key=lambda x: x["size"], reverse=True)
        return trending
    
    def get_most_trending_topic(self, min_size: int = 3) -> Optional[Dict[str, Any]]:
        """Get the most trending topic (largest cluster) if it's meaningful"""
        if not self.clusters:
            logging.warning("No clusters available")
            return None
        
        # Get trending topics
        trending = self.get_trending_topics(min_size)
        
        if not trending:
            logging.warning("No trending topics found")
            return None
        
        # Get the largest cluster
        most_trending = trending[0]
        
        # Check if the topic is meaningful (has good keywords and reasonable size)
        if (most_trending['size'] >= min_size and 
            len(most_trending['keywords']) >= 3 and
            most_trending['avg_probability'] > 0.7):
            
            # Get the posts for this topic
            topic_posts = self.get_cluster_posts(most_trending['topic_id'])
            
            return {
                'topic_info': most_trending,
                'posts': topic_posts
            }
        
        logging.info("Most trending topic is not meaningful enough")
        return None

    def generate_trending_topic_report(self, min_size: int = 3) -> Optional[str]:
        """Generate a report for the most trending topic using LLM"""
        try:
            # Get the most trending topic
            trending_data = self.get_most_trending_topic(min_size)
            
            if not trending_data:
                logging.warning("No meaningful trending topic found for report generation")
                return None
            
            topic_info = trending_data['topic_info']
            posts = trending_data['posts']
            
            # Sort posts by probability (highest first) and take top 3
            sorted_posts = sorted(posts, key=lambda x: x['probability'], reverse=True)[:3]
            
            # Extract cleaned_text from top 3 posts
            post_texts = []
            for post_data in sorted_posts:
                post = post_data['post']
                if post.cleaned_text and post.cleaned_text.strip():
                    post_texts.append({
                        'title': post.title,
                        'content': post.cleaned_text,
                        'source': post.source,
                        'probability': post_data['probability']
                    })
            
            if not post_texts:
                logging.warning("No valid cleaned_text found in top posts")
                return None
            
            # Prepare the prompt for LLM
            prompt = self._create_report_prompt(topic_info, post_texts)
            
            # Generate report using LLM (synchronous)
            logging.info("Generating report using LLM...")
            report = asyncio.run(self.llm.get_completion(prompt))
            
            logging.info("Report generated successfully")
            return report
            
        except Exception as e:
            logging.error(f"Error generating trending topic report: {e}")
            raise

    def _create_report_prompt(self, topic_info: Dict[str, Any], post_texts: List[Dict[str, Any]]) -> str:
        """Create a prompt for the LLM to generate a report"""
        
        try:
            # Format the post texts
            posts_content = ""
            for i, post in enumerate(post_texts, 1):
                posts_content += f"""
                                    Post {i}:
                                    Title: {post.get('title', 'No title')}
                                    Source: {post.get('source', 'Unknown')}
                                    Content: {post.get('content', 'No content')[:1000]}...  # Truncate to avoid token limits
                                    """
            
            # Pre-format the topic_info values to avoid KeyError in string formatting
            topic_id = topic_info.get('topic_id', 'Unknown')
            size = topic_info.get('size', 0)
            keywords = topic_info.get('keywords', [])
            sources = topic_info.get('sources', [])
            avg_probability = topic_info.get('avg_probability', 0.0)
            
            # Format keywords and sources as strings
            keywords_str = ', '.join(keywords) if keywords else 'None'
            sources_str = ', '.join(sources) if sources else 'None'
            
            # Create the formatted prompt
            prompt = SOCIAL_PROMPT.format(
                topic_id=topic_id,
                size=size,
                posts_content=posts_content,
                keywords_str=keywords_str,
                sources_str=sources_str,
                avg_probability=avg_probability
            )
            
            return prompt
            
        except Exception as e:
            logging.error(f"Error creating report prompt: {e}")
            # Return a fallback prompt
            return f"""
You are a social media analyst. Please write a brief report about the following content.

Content: {str(post_texts)[:1000]}...

Please provide a 2-3 sentence summary of the main trends or topics discussed in this content.
"""

    def export_clusters(self, output_file: str = "clusters_analysis.json"):
        """Export clustering results to JSON file"""
        if not self.clusters:
            logging.warning("No clusters to export")
            return
        
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "clusters": self.clusters,
                "analysis": self.cluster_analysis
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logging.info(f"Clusters exported to {output_file}")
            
        except Exception as e:
            logging.error(f"Error exporting clusters: {e}")
            raise

    def analyze_social_trends(self, state: State, days_back: int = 30) -> State:
        """Main method to run complete social analysis and update state"""
        try:
            logging.info("Starting social analysis...")
            
            # Get posts from database
            posts = self.get_all_posts(days_back)
            
            if not posts:
                logging.warning("No posts found for analysis")
                return state
            
            # Preprocess titles
            titles, valid_posts = self.preprocess_titles(posts)
            
            if not titles:
                logging.warning("No valid titles found for clustering")
                return state
            
            # Perform clustering
            clusters = self.perform_clustering(titles, valid_posts)
            
            # Check if clustering was successful
            if not clusters or clusters.get("total_clusters", 0) == 0:
                logging.warning("Clustering failed or returned no clusters, skipping analysis")
                return state
            
            # Analyze clusters
            analysis = self.analyze_clusters()
            
            # Generate trending topic report
            report = self.generate_trending_topic_report(min_size=10)
            
            # Update state with social analysis results
            if report:
                topic = HotTopic(
                    id=str(uuid.uuid4()),
                    snippet=report,
                    publication_date=datetime.now(timezone.utc),
                )
                
                state.hot_topics.append(topic)
                logging.info("Added hot topic to state")
            else:
                logging.warning("No trending topic report generated")
            
            # Export results
            self.export_clusters()
            
            logging.info("Social analysis completed successfully")
            return state
            
        except Exception as e:
            logging.error(f"Error in social analysis: {e}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            # Return state even if analysis fails
            return state
        finally:
            if hasattr(self, 'db') and self.db.session:
                self.db.session.close()


def analyze_social_trends(state: State, llm: AIClient) -> State:
    """Entry point function for the social agent system."""
    analyzer = SocialAnalyzer(llm)
    return analyzer.analyze_social_trends(state)


if __name__ == "__main__":
    # Test the social agent
    from utils.ai_client import AIClient
    
    llm = AIClient()
    state = State()
    result = analyze_social_trends(state, llm)
    print("Social analysis completed")


