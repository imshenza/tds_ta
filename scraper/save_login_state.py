from playwright.sync_api import sync_playwright

def save_login_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://tds.s-anand.net")

        print("👉 Please log in manually in the opened browser window.")
        print("⏳ Waiting for 60 seconds...")
        page.wait_for_timeout(60000)  # wait 60 seconds for manual login

        print("💾 Saving login session to auth_course.json")
        context.storage_state(path="auth_course.json")

        browser.close()

if __name__ == "__main__":
    save_login_state()
