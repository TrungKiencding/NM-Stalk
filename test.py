from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
def fb_scrage():
    urls = ["https://www.facebook.com/cung.AI.VN"]
    MAX_POSTS = 5
    seen_texts = set()
    posts = []
    links = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        try:
            context = browser.new_context(storage_state="fb_state.json")
        except:
            context = browser.new_context()

        page = context.new_page()  

        #login
        page.goto("https://www.facebook.com/")
        try:
            page.wait_for_selector('[data-testid="royal-email"]', timeout=500)
            page.get_by_role("button", name="Allow all cookies").click()
            time.sleep(3)
        except:
            pass
        try:
            page.wait_for_selector('[data-testid="royal-email"]', timeout=500)
            page.get_by_test_id("royal-email").click()
            page.get_by_test_id("royal-email").fill("lk4trungkien@gmail.com")
            page.locator("#passContainer").click()
            time.sleep(3)
            page.wait_for_selector('[data-testid="royal-pass"]', timeout=500)
            page.get_by_test_id("royal-pass").fill("trungkien123")
            time.sleep(3)
            page.get_by_test_id("royal-pass").press("Enter")
        except:
            pass

        time.sleep(3)
        for url in urls:
            all_posts = []
            page.goto(url)
            while len(all_posts) < 5:
                soup = BeautifulSoup(page.content(), "html.parser")
            #get containers of posts    
                containers = soup.find_all(
                lambda tag: (
                    tag.name == "div"
                    and (
                        tag.get("data-ad-comet-preview") == "message"
                        or tag.get("data-ad-rendering-role") == "story_message"
                    )
                )
            )
            # Extract the full caption per post
                for container in containers:
                    # full text: keep line-breaks so bullet lists stay readable
                    post_text = container.get_text(separator="\n", strip=True)

                    # filter duplicates / very short blurbs
                    if (
                        post_text
                        and len(post_text.split()) > 105    
                        and post_text not in seen_texts      
                        and "See more" not in post_text
                    ):
                        print(f"\n📝 {post_text}…")          
                        posts.append(post_text)
                        links.append(url)
                    
                    #list to track for break condition of each link
                        all_posts.append(post_text)
                        seen_texts.add(post_text)

                        if len(all_posts) >= MAX_POSTS:
                            break

                print(f"🔃 Scrolling for more... (collected {len(all_posts)} so far)")
                
                #click on See more for full content visibility
                see_more_buttons = page.locator("text='See more'")
                for i in range(see_more_buttons.count()):
                    try:
                        see_more_buttons.nth(i).click(timeout=2000)
                        page.wait_for_load_state()
                    except:
                        pass
                
                #scroll for more contents
                box = page.viewport_size
                if box:
                        scroll_height = int(box['height']) + 50
                        page.mouse.wheel(0, scroll_height)
                        page.wait_for_load_state()  # short wait for content to render
        browser.close()
    print(f"✅ Done: Scraped {len(all_posts)} unique posts.")

    return posts, links


posts, links = fb_scrage()