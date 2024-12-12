## the journey of a thousand miles begins with a step

from playwright.sync_api import sync_playwright
import time


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # access kenya law
        page=context.new_page()
        page.goto("https://kenyalaw.org/kenyalawblog/introducing-the-new-kenya-law-website/")

        # page content
        html_content = page.content()

        with open("kenyalaw.html","w+",encoding="utf8") as kFIle:
            kFIle.write(html_content)

        getCauseListAll(page)
    
def getCauseListAll(page):
    try:
        page.click("//a[normalize-space()='Cause List']")

        time.sleep(5)

         # Locate all anchor tags inside the specific div
        anchor_elements = page.locator("div.flow-columns.mb-3 a")
        count = anchor_elements.count()
        print(f"Found {count} anchor tags inside the div.")

        # Click each anchor tag sequentially
        for i in range(count):
            href = anchor_elements.nth(i).get_attribute("href")  # Retrieve the href attribute
            print(f"Clicking on: {href}")
            anchor_elements.nth(i).click()
            page.wait_for_load_state("domcontentloaded")  # Wait for potential navigation
            page.go_back()  # Navigate back to the original page if needed

        # Close the browser
        page.close()
    except Exception as e :
        print("The error getting the cause list is $$",str(e))


if(__name__ == "__main__"):
    main()