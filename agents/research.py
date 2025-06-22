import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.models import State, Item, Post
from datetime import datetime, timezone, timedelta
import logging
import uuid
from typing import List, Dict

from tools.search_tools import SearchTools
from tools.content_extractor import ContentExtractor
from crawlers.github_crawler import GitHubCrawler
from crawlers.arxiv_crawler import ArXivCrawler
from crawlers.facebook_crawler import FacebookCrawler
from crawlers.X_crawler import XCrawler
from config import Config

class ResearchCrawler:
    def __init__(self):
        self.search_tools = SearchTools()
        self.content_extractor = ContentExtractor()
        self.github_crawler = GitHubCrawler()
        self.arxiv_crawler = ArXivCrawler()
        self.facebook_crawler = FacebookCrawler()
        self.x_crawler = XCrawler()


    def crawl_data(self, state: State) -> State:
        """Main crawling function that combines GitHub, arXiv, and Facebook data with enrichment."""
        try:
            # Get trending GitHub repositories
            try:
                repos = self.github_crawler.fetch_trending_repos(max_repos=Config.GITHUB_MAX_REPOS)
                github_items = []
                
                for repo in repos:
                    data = self.github_crawler.grab_readme(repo)
                    if data["content"]:
                        item = Item(
                            id=str(uuid.uuid4()),
                            url=f"https://github.com/{repo}",
                            title=repo,
                            content_snippet=data["content"],
                            publication_date=datetime.now(timezone.utc),
                            source="GitHub",
                            timestamp=datetime.now(timezone.utc),
                        )
                        github_items.append(item)
            except Exception as e:
                logging.error(f"Error fetching GitHub repositories: {e}")


            # Get recent arXiv papers (last 24 hours)
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=1)
            links, abstracts, titles = self.arxiv_crawler.get_papers_by_subject_and_dates(
                subjects=Config.ARXIV_SUBJECT, 
                start=start,
                end=end,
                max_results=Config.ARXIV_MAX_RESULTS
            )

            arxiv_items = []
            for link, abstract, title in zip(links, abstracts, titles):
                item = Item(
                    id=str(uuid.uuid4()),
                    url=link,
                    title=title,
                    content_snippet=abstract,
                    publication_date=datetime.now(timezone.utc),
                    source="arXiv",
                    timestamp=datetime.now(timezone.utc),
                )
                arxiv_items.append(item)
                
            # Get Facebook posts
            facebook_posts = []
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
                            post = Post(
                                id=str(uuid.uuid4()),
                                title=None,  
                                content_snippet=post,
                                publication_date=datetime.now(timezone.utc),
                                source="Facebook",
                                timestamp=datetime.now(timezone.utc),
                            )
                            facebook_posts.append(post)
                    except Exception as e:
                        logging.error(f"Error crawling Facebook page {page_url}: {e}")
           
           
            # Get X posts
            x_posts = []
            if hasattr(Config, 'X_PAGES') and Config.X_PAGES:
                for page_url in Config.X_PAGES:
                    posts, links, _ = self.x_crawler.get_posts_from_page(
                        page_url=page_url,
                        max_posts=Config.MAX_X_POSTS)
                    for post, link in zip(posts, links):
                        post = Post(
                            id=str(uuid.uuid4()),
                            url=link,
                            title=None,  
                            content_snippet=post,
                            publication_date=datetime.now(timezone.utc),
                            source="X",
                            timestamp=datetime.now(timezone.utc),
                        )
                        x_posts.append(post)

            # Combine all items
            state.items.extend(github_items)
            state.items.extend(arxiv_items)
            state.posts.extend(facebook_posts)
            state.posts.extend(x_posts)

       
            logging.info(f"Crawled {len(github_items)} GitHub repos, {len(arxiv_items)} arXiv papers, {len(facebook_posts)} Facebook posts, and {len(x_posts)} X posts")
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