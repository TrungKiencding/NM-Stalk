import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.models import State, Item
from datetime import datetime, timezone, timedelta
import logging
import uuid
from typing import List, Dict

from tools.search_tools import SearchTools
from tools.content_extractor import ContentExtractor
from crawlers.github_crawler import GitHubCrawler
from crawlers.arxiv_crawler import ArXivCrawler

class ResearchCrawler:
    def __init__(self):
        self.search_tools = SearchTools()
        self.content_extractor = ContentExtractor()
        self.github_crawler = GitHubCrawler()
        self.arxiv_crawler = ArXivCrawler()

    def enrich_content(self, content: str, max_related: int = 3) -> List[Dict[str, str]]:
        """
        Find related content using Google search.
        Returns list of {"link": url, "raw_content": content} dicts.
        """
        try:
            # Search for related content
            search_results = self.search_tools.google_search(content, num=max_related)
            if not search_results or 'items' not in search_results:
                return []

            # Extract URLs from search results
            urls = [item['link'] for item in search_results.get('items', [])]
            
            # Extract content from URLs
            return self.content_extractor.extract_content_sync(urls)
        except Exception as e:
            logging.error(f"Error enriching content: {e}")
            return []

    def crawl_data(self, state: State) -> State:
        """Main crawling function that combines GitHub and arXiv data with enrichment."""
        try:
            # Get trending GitHub repositories
            repos = self.github_crawler.fetch_trending_repos(max_repos=5)
            github_items = []
            
            for repo in repos:
                data = self.github_crawler.grab_readme(repo)
                if data["content"]:
                    # Get related content
                    related_content = self.enrich_content(data["content"][:500])  # Use first 500 chars for search
                    
                    item = Item(
                        id=str(uuid.uuid4()),
                        url=f"https://github.com/{repo}",
                        title=repo,
                        content_snippet=data["content"][:1000],
                        publication_date=datetime.now(timezone.utc),
                        source="GitHub",
                        timestamp=datetime.now(timezone.utc),
                        related_content=related_content
                    )
                    github_items.append(item)

            # Get recent arXiv papers (last 24 hours)
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=1)
            links, abstracts, titles = self.arxiv_crawler.get_papers_by_subject_and_dates(
                subject="cs.AI",  # Computer Science - Artificial Intelligence
                start=start,
                end=end,
                max_results=5
            )

            arxiv_items = []
            for link, abstract, title in zip(links, abstracts, titles):
                # Get related content
                related_content = self.enrich_content(abstract)
                
                item = Item(
                    id=str(uuid.uuid4()),
                    url=link,
                    title=title,
                    content_snippet=abstract,
                    publication_date=datetime.now(timezone.utc),
                    source="arXiv",
                    timestamp=datetime.now(timezone.utc),
                    related_content=related_content
                )
                arxiv_items.append(item)

            # Combine all items
            state.items.extend(github_items)
            state.items.extend(arxiv_items)
            
            logging.info(f"Crawled {len(github_items)} GitHub repos and {len(arxiv_items)} arXiv papers")
            return state
        except Exception as e:
            logging.error(f"Crawl data failed: {e}")
            raise

def crawl_data(state: State) -> State:
    """Entry point function for the agent system."""
    crawler = ResearchCrawler()
    return crawler.crawl_data(state) 