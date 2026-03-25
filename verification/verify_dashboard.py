from playwright.sync_api import sync_playwright, expect

def test_dashboard(page):
    page.goto("http://localhost:3000")
    # Wait for the Stability Score card to be visible
    page.wait_for_selector("text=Stability Score")
    # Take a screenshot
    page.screenshot(path="verification/dashboard.png")
    print("Screenshot saved to verification/dashboard.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_dashboard(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
