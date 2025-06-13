from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

BASE_URL = "https://tds.s-anand.net/#/"
OUTPUT_DIR = "./data/tds_course"

def sanitize_filename(name):
    return name.replace("/", "-").replace("\\", "-").replace(" ", "_").strip()

def scrape_all_pages():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print("🌐 Navigating to course homepage...")
        page.goto(BASE_URL)
        page.wait_for_timeout(4000)

        print("📋 Extracting sidebar links...")
        page.wait_for_selector(".sidebar-nav")
        links = page.eval_on_selector_all(
            ".sidebar-nav a",
            "elements => elements.map(el => ({ href: el.href, text: el.textContent }))"
        )

        print(f"🔗 Found {len(links)} links")

        for link in links:
            href = link["href"]
            title = sanitize_filename(link["text"])
            print(f"🧭 Visiting {href} → {title}.md")

            page.goto(href)
            page.wait_for_timeout(3000)

            try:
                html = page.inner_html("article.markdown-section")
                soup = BeautifulSoup(html, "html.parser")
                content = soup.get_text(separator="\n")

                file_path = os.path.join(OUTPUT_DIR, f"{title}.md")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Saved: {file_path}")
            except Exception as e:
                print(f"⚠️ Failed to extract {href}: {e}")

        browser.close()
        print("🎉 Finished scraping all pages!")

if __name__ == "__main__":
    scrape_all_pages()
