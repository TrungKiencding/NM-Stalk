from datetime import datetime
import feedparser
from typing import List, Tuple
import logging

class ArXivCrawler:
    @staticmethod
    def get_papers_by_subject_and_dates(
        subject: str,
        start: datetime,
        end: datetime,
        max_results: int = 50
    ) -> Tuple[List[str], List[str]]:
        """
        Query arXiv for papers in `subject` whose submission times fall
        between `start` and `end` (both datetimes in UTC).
        Returns a tuple of (links, abstracts).
        """
        try:
            # Format datetimes as YYYYMMDDHHMM (GMT)
            fmt = "%Y%m%d%H%M"
            start_s = start.strftime(fmt)
            end_s = end.strftime(fmt)

            # Build the search_query string
            date_filter = f"submittedDate:[{start_s}+TO+{end_s}]"
            query = f"cat:{subject}+AND+{date_filter}"

            # Construct the full API URL
            base_url = "http://export.arxiv.org/api/query?"
            url = (
                f"{base_url}"
                f"search_query={query}"
                f"&start=0"
                f"&max_results={max_results}"
                f"&sortBy=submittedDate"
                f"&sortOrder=descending"
            )

            # Fetch and parse the Atom feed
            feed = feedparser.parse(url)
            links = []
            abstracts = []
            titles = []
            for entry in feed.entries:
                links.append(entry.id)
                abstracts.append(entry.summary.strip().replace("\n", " "))
                titles.append(entry.title)
            return links, abstracts, titles
        except Exception as e:
            logging.error(f"Error fetching arXiv papers: {e}")
            return [], [], [] 