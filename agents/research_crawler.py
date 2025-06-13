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
from crawlers.facebook_crawler import FacebookCrawler
from config import Config

class ResearchCrawler:
    def __init__(self):
        self.search_tools = SearchTools()
        self.content_extractor = ContentExtractor()
        self.github_crawler = GitHubCrawler()
        self.arxiv_crawler = ArXivCrawler()
        self.facebook_crawler = FacebookCrawler()

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
        """Main crawling function that combines GitHub, arXiv, and Facebook data with enrichment."""
        try:
            # Get trending GitHub repositories
            repos = self.github_crawler.fetch_trending_repos(max_repos=Config.GITHUB_MAX_REPOS)
            github_items = []
            
            for repo in repos:
                data = self.github_crawler.grab_readme(repo)
                if data["content"]:
                    # Get related content
                    #related_content = self.enrich_content(data["content"][:500])  # Use first 500 chars for search
                    related_content = []
                    item = Item(
                        id=str(uuid.uuid4()),
                        url=f"https://github.com/{repo}",
                        title=repo,
                        content_snippet=data["content"],
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
                subject=Config.ARXIV_SUBJECT, 
                start=start,
                end=end,
                max_results=Config.ARXIV_MAX_RESULTS
            )

            arxiv_items = []
            for link, abstract, title in zip(links, abstracts, titles):
                # Get related content
                #related_content = self.enrich_content(abstract)
                related_content = []
                
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

            # Get Facebook posts
            facebook_items = []
            if hasattr(Config, 'FACEBOOK_PAGES') and Config.FACEBOOK_PAGES:
                for page_url in Config.FACEBOOK_PAGES:
                    try:
                        posts, links, _ = self.facebook_crawler.get_posts_from_page(
                            page_url=page_url,
                            max_posts=Config.MAX_FACEBOOK_POSTS,
                            email=getattr(Config, 'FACEBOOK_EMAIL', None),
                            password=getattr(Config, 'FACEBOOK_PASSWORD', None)
                        )
                        
                        for post, link in zip(posts, links):
                            # Get related content
                            #related_content = self.enrich_content(post[:500])  # Use first 500 chars for search
                            related_content = []
                            
                            item = Item(
                                id=str(uuid.uuid4()),
                                url=link,
                                title=None,  
                                content_snippet=post,
                                publication_date=datetime.now(timezone.utc),
                                source="Facebook",
                                timestamp=datetime.now(timezone.utc),
                                related_content=related_content
                            )
                            facebook_items.append(item)
                    except Exception as e:
                        logging.error(f"Error crawling Facebook page {page_url}: {e}")

            # Combine all items
            state.items.extend(github_items)
            state.items.extend(arxiv_items)
            state.items.extend(facebook_items)
            
            for item in state.items:
                print(item.title)
                print(item.url)
                print(item.content_snippet)
                print(item.related_content)
                print("-"*100)
                
            logging.info(f"Crawled {len(github_items)} GitHub repos, {len(arxiv_items)} arXiv papers, and {len(facebook_items)} Facebook posts")
            return state
        except Exception as e:
            logging.error(f"Crawl data failed: {e}")
            raise

def crawl_data(state: State) -> State:
    """Entry point function for the agent system."""
    crawler = ResearchCrawler()
    return crawler.crawl_data(state) 

if __name__ == "__main__":
    state = State()
    crawl_data(state)