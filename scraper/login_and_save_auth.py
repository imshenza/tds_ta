from playwright.sync_api import sync_playwright

def login_and_save_auth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # we want the browser visible
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://discourse.onlinedegree.iitm.ac.in/")

        print("⚠️ Please manually log in using the browser window.")
        print("After you log in completely, close the browser tab.")
        input("✅ Press Enter here once you're logged in and ready to save auth...")

        context.storage_state(path="auth.json")
        print("✅ Login session saved to auth.json")

        browser.close()

if __name__ == "__main__":
    login_and_save_auth()
