from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os
import time

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"
OUTPUT_FILE = "data/discourse_posts.json"
DEBUG_FILE = "debug_topic_page.html"

def save_html_for_debug(page_content):
    with open(DEBUG_FILE, "w", encoding="utf-8") as f:
        f.write(page_content)

def extract_topic_links(page_content):
    soup = BeautifulSoup(page_content, "html.parser")
    topic_links = []

    for a in soup.select("a[href*='/t/']"):
        href = a.get("href")
        if href and href.startswith("/t/") and href not in topic_links:
            topic_links.append("https://discourse.onlinedegree.iitm.ac.in" + href)

    return topic_links

def extract_post_data(page_content):
    soup = BeautifulSoup(page_content, "html.parser")
    posts = []
    for div in soup.select("div.topic-body"):
        content = div.get_text(strip=True, separator="\n")
        posts.append(content)
    return posts

def scrape_all():
    print("🚀 Launching browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="auth.json")  
        page = context.new_page()

        print("🌐 Visiting TDS Discourse page...")
        page.goto(BASE_URL)
        time.sleep(5)  

        html = page.content()
        save_html_for_debug(html)

        topic_links = extract_topic_links(html)
        print(f"🔍 Found {len(topic_links)} topics")

        if not topic_links:
            print("⚠️ No topics found. Check debug_topic_page.html to verify what was rendered.")
            return

        all_posts = []

        for idx, link in enumerate(topic_links):
            print(f"📄 Scraping topic {idx+1}/{len(topic_links)}: {link}")
            page.goto(link)
            time.sleep(3)
            post_html = page.content()
            posts = extract_post_data(post_html)
            all_posts.append({
                "url": link,
                "posts": posts
            })

        print(f"💾 Saving {len(all_posts)} topics to {OUTPUT_FILE}")
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_posts, f, indent=2, ensure_ascii=False)

        browser.close()
        print("✅ Done.")

if __name__ == "__main__":
    scrape_all()
