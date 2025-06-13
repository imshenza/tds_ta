from playwright.sync_api import sync_playwright

def save_login_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("🌐 Opening course website...")
        page.goto("https://tds.s-anand.net", timeout=60000)

        print("🔐 Please log in manually (e.g., enter email, OTP)")
        print("⏳ You have 2 minutes to complete the login.")
        page.wait_for_timeout(120000)  # wait 2 minutes for you to login

        print("💾 Saving login session to auth_course.json...")
        context.storage_state(path="auth_course.json")
        browser.close()

if __name__ == "__main__":
    save_login_state()
