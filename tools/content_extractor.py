from typing import List, Dict
import logging
from crawl4ai import AsyncWebCrawler
import asyncio

class ContentExtractor:
    @staticmethod
    async def extract_content(urls: List[str]) -> List[Dict[str, str]]:
        """
        Extract content from URLs using crawl4ai.
        Args:
            urls: List of URLs to extract content from
        Returns:
            List of dicts with 'link' and 'raw_content'
        """
        try:
            results = []
            async with AsyncWebCrawler() as crawler:
                crawl_results = await crawler.arun_many(urls)
                for result in crawl_results:
                    if result.success:
                        results.append({
                            "link": result.url,
                            "raw_content": result.markdown
                        })
                    else:
                        results.append({
                            "link": result.url,
                            "raw_content": "[FAILED to crawl]"
                        })
            return results
        except Exception as e:
            logging.error(f"Content extraction failed: {e}")
            return []

    @staticmethod
    def extract_content_sync(urls: List[str]) -> List[Dict[str, str]]:
        """
        Synchronous wrapper for extract_content.
        """
        return asyncio.run(ContentExtractor.extract_content(urls)) 