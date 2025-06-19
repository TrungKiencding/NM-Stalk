from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
import logging
from typing import List, Tuple, Optional
from datetime import datetime
import os
import shutil

class XCrawler:
    STATE_FILE = "X_state.json"
    
    @staticmethod
    def save_login_state(context) -> None:
        """Save the X (Twitter) login state to a file."""
        try:
            context.storage_state(path=XCrawler.STATE_FILE)
            logging.info("Successfully saved X login state")
        except Exception as e:
            logging.error(f"Failed to save X login state: {e}")

    @staticmethod
    def get_posts_from_page(
        page_url: str,
        max_posts: int = 5,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Crawl posts from an X (Twitter) page.
        
        Args:
            page_url: URL of the X page to crawl
            max_posts: Maximum number of posts to collect
            email: X login email (optional)
            password: X login password (optional)
            
        Returns:
            Tuple of (posts, links, titles) where:
            - posts is a list of post contents
            - links is a list of corresponding page URLs
            - titles is a list of post titles (empty for X as posts don't have titles)
        """
        urls = [page_url]
        seen_texts = set()
        posts = []
        links = []
        titles = []  # X posts don't have titles, but we keep this for consistency
        
        try:
            chrome_path = shutil.which("google-chrome") or shutil.which("chrome")
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,
                    executable_path=chrome_path,
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
                logging.info("Launching Playwright browser")
                
                try:
                    if os.path.exists(XCrawler.STATE_FILE):
                        context = browser.new_context(storage_state=XCrawler.STATE_FILE)
                        logging.info("Using existing X login state")
                    else:
                        context = browser.new_context()
                        logging.info("No existing X login state found")
                except Exception as e:
                    logging.warning(f"Failed to load X state: {e}")
                    context = browser.new_context()

                page = context.new_page()
                for url in urls:
                    all_posts = []
                    try:
                        page.goto(url)
                        page.wait_for_load_state()
                        logging.info(f"Visiting page: {url}")
                    except Exception as e:
                        logging.error(f"Failed to load page {url}: {e}")
                        continue

                    while len(all_posts) < max_posts:
                        try:
                            # Click on See more for full content visibility
                            see_more_buttons = page.locator("button[data-testid='tweet-text-show-more-link']")
                            for i in range(see_more_buttons.count()):
                                try:
                                    see_more_buttons.nth(i).click(timeout=2000)
                                    page.wait_for_load_state()
                                    time.sleep(3)
                                except Exception as e:
                                    logging.info(f"Failed to click 'See more' button: {e}")

                            soup = BeautifulSoup(page.content(), "html.parser")
                            # Get containers of posts
                            logging.info("Parsing page content for posts")
                            containers = soup.find_all(
                                lambda tag: (
                                    tag.name == "div"
                                    and (
                                        tag.get("dir") == "auto"
                                        and tag.get("data-testid") == "tweetText"
                                    )
                                )
                            )

                            # Extract the full caption per post
                            for container in containers:
                                post_text = container.get_text(separator="\n", strip=True)

                                if (
                                    post_text
                                    and post_text not in seen_texts
                                    and "Show more" not in post_text
                                ):
                                    posts.append(post_text)
                                    links.append(url)
                                    titles.append("")  # Empty title for consistency
                                    all_posts.append(post_text)
                                    seen_texts.add(post_text)

                                    if len(all_posts) >= max_posts:
                                        break

                            # Scroll for more contents
                            box = page.viewport_size
                            if box:
                                scroll_height = int(box['height']) + 50
                                page.mouse.wheel(0, scroll_height)
                                page.wait_for_load_state()
                        except Exception as e:
                            logging.error(f"Error processing page content: {e}")
                            break

                browser.close()
                
            return posts, links, titles
            
        except Exception as e:
            logging.error(f"Error crawling X page: {e}")
            return [], [], [] 