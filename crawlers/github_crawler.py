import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import time

class GitHubCrawler:
    TRENDING_URL = "https://github.com/trending?since=daily"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    @staticmethod
    def fetch_trending_repos(max_repos: int = 20) -> List[str]:
        """Return a list like ["owner1/repo1", "owner2/repo2", …]."""
        try:
            resp = requests.get(GitHubCrawler.TRENDING_URL, headers=GitHubCrawler.HEADERS, timeout=15)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("article.Box-row h2 a")  # repo links
            repos = []
            for a in links[:max_repos]:
                repo_path = a["href"].strip("/")
                repos.append(repo_path)
            return repos
        except Exception as e:
            logging.error(f"Error fetching trending repos: {e}")
            return []

    @staticmethod
    def grab_readme(owner_repo: str) -> Dict[str, str]:
        """
        Attempt to fetch the raw README from the repo's default branch.
        Returns dict {"repo": "<owner/repo>", "url": "<raw-url>", "content": "<md or ''>"}
        """
        try:
            owner, repo = owner_repo.split("/")
            branches = ["main", "master"]
            content = ""
            raw_url = ""
            for br in branches:
                url = f"https://raw.githubusercontent.com/{owner}/{repo}/{br}/README.md"
                r = requests.get(url, headers=GitHubCrawler.HEADERS, timeout=15)
                if r.status_code == 200 and r.text.strip():
                    raw_url = url
                    content = r.text
                    break
                time.sleep(1)  # Be polite to GitHub
            return {"repo": owner_repo, "url": raw_url, "content": content}
        except Exception as e:
            logging.error(f"Error grabbing README for {owner_repo}: {e}")
            return {"repo": owner_repo, "url": "", "content": ""} 