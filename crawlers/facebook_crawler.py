from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
import logging
from typing import List, Tuple, Optional
from datetime import datetime
import os

class FacebookCrawler:
    STATE_FILE = "facebook_state/fb_state.json"
    
    @staticmethod
    def save_login_state(context) -> None:
        """Save the Facebook login state to a file."""
        try:
            context.storage_state(path=FacebookCrawler.STATE_FILE)
            logging.info("Successfully saved Facebook login state")
        except Exception as e:
            logging.error(f"Failed to save Facebook login state: {e}")

    @staticmethod
    def get_posts_from_page(
        page_url: str,
        max_posts: int = 5,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Crawl posts from a Facebook page.
        
        Args:
            page_url: URL of the Facebook page to crawl
            max_posts: Maximum number of posts to collect
            email: Facebook login email (optional)
            password: Facebook login password (optional)
            
        Returns:
            Tuple of (posts, links, titles) where:
            - posts is a list of post contents
            - links is a list of corresponding page URLs
            - titles is a list of post titles (empty for Facebook as posts don't have titles)
        """
        urls = [page_url]
        seen_texts = set()
        posts = []
        links = []
        titles = []  # Facebook posts don't have titles, but we keep this for consistency
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    if os.path.exists(FacebookCrawler.STATE_FILE):
                        context = browser.new_context(storage_state=FacebookCrawler.STATE_FILE)
                        logging.info("Using existing Facebook login state")
                    else:
                        context = browser.new_context()
                        logging.info("No existing Facebook login state found")
                except Exception as e:
                    logging.warning(f"Failed to load Facebook state: {e}")
                    context = browser.new_context()

                page = context.new_page()

                # Login if credentials provided
                if email and password:
                    try:
                        page.goto("https://www.facebook.com/")
                        # Handle cookie consent
                        try:
                            page.wait_for_selector('[data-testid="royal-email"]', timeout=500)
                            page.get_by_role("button", name="Allow all cookies").click()
                            time.sleep(3)
                        except Exception as e:
                            pass

                        # Perform login
                        try:
                            page.wait_for_selector('[data-testid="royal-email"]', timeout=500)
                            page.get_by_test_id("royal-email").click()
                            page.get_by_test_id("royal-email").fill(email)
                            page.locator("#passContainer").click()
                            time.sleep(3)
                            page.wait_for_selector('[data-testid="royal-pass"]', timeout=500)
                            page.get_by_test_id("royal-pass").fill(password)
                            time.sleep(3)
                            page.get_by_test_id("royal-pass").press("Enter")
                            time.sleep(3)
                        except Exception as e:
                            pass
                        FacebookCrawler.save_login_state(context)
                        logging.info("Successfully logged in to Facebook")
                    except Exception as e:
                        logging.error(f"Facebook login failed: {e}")
                        return [], [], []

                for url in urls:
                    all_posts = []
                    try:
                        page.goto(url)
                    except Exception as e:
                        logging.error(f"Failed to load page {url}: {e}")
                        continue

                    while len(all_posts) < max_posts:
                        try:
                            soup = BeautifulSoup(page.content(), "html.parser")
                            # Get containers of posts    
                            containers = soup.find_all(
                                lambda tag: (
                                    tag.name == "div"
                                    and (
                                        tag.get("data-ad-comet-preview") == "message"
                                        or tag.get("data-ad-rendering-role") == "story_message"
                                    )
                                )
                            )
                            
                            if not containers:
                                logging.warning("No post containers found on page")
                                break

                            # Extract the full caption per post
                            for container in containers:
                                post_text = container.get_text(separator="\n", strip=True)

                                if (
                                    post_text
                                    and len(post_text.split()) > 105    
                                    and post_text not in seen_texts      
                                    and "See more" not in post_text
                                ):
                                    posts.append(post_text)
                                    links.append(url)
                                    titles.append("")  # Empty title for consistency
                                    all_posts.append(post_text)
                                    seen_texts.add(post_text)

                                    if len(all_posts) >= max_posts:
                                        break

                            # Click on See more for full content visibility
                            see_more_buttons = page.locator("text='See more'")
                            for i in range(see_more_buttons.count()):
                                try:
                                    see_more_buttons.nth(i).click(timeout=2000)
                                    page.wait_for_load_state()
                                except Exception as e:
                                    logging.debug(f"Failed to click 'See more' button: {e}")
                            
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
                
            logging.info(f"✅ Done: Scraped {len(all_posts)} unique posts.")
            return posts, links, titles
            
        except Exception as e:
            logging.error(f"Error crawling Facebook page: {e}")
            return [], [], [] 