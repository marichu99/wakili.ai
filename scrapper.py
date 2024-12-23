import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

# Define the downloads folder path
downloads_folder = Path.home() / "Documents" / "causelists"
downloads_folder.mkdir(parents=True, exist_ok=True)  # Create folder if not exists
def main():
    

    with sync_playwright() as p:
        # Launch browser with downloads enabled
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)  # No download_path here

        # Access Kenya Law website
        page = context.new_page()
        page.goto("https://kenyalaw.org/kenyalawblog/introducing-the-new-kenya-law-website/", timeout=60000)

        # Save the initial page content
        html_content = page.content()
        with open("kenyalaw.html", "w+", encoding="utf8") as kFIle:
            kFIle.write(html_content)

        time.sleep(6)
        # Get Cause List
        get_cause_list_all(page)

        # Close the browser
        browser.close()

def get_cause_list_all(page):
    try:
        # Click the 'Cause List' link
        page.click("//a[normalize-space()='Cause List']")
        page.wait_for_selector("div.flow-columns.mb-3 a")  # Wait for the links to load

        # Locate all anchor tags inside the specific div
        anchor_elements = page.locator("div.flow-columns.mb-3 a")
        count = anchor_elements.count()
        print(f"Found {count} anchor tags inside the div.")

        # Click each anchor tag sequentially
        for i in range(count):
            href = anchor_elements.nth(i).get_attribute("href")
            print(f"Clicking on: {href}")
            anchor_elements.nth(i).click()
            page.wait_for_selector("//label[normalize-space()='Monthly Cause List']")  # Wait for filter

            # Filter cause list content
            page.click("//label[normalize-space()='Monthly Cause List']")
            
            click_table_anchors(page)

            page.go_back()  # Navigate back to the main page
            page.wait_for_selector("div.flow-columns.mb-3 a")  # Ensure links reload

    except Exception as e:
        print("Error getting the cause list:", str(e))

def click_table_anchors(page):
    # Wait for the table to load
    page.wait_for_selector("div.table-responsive#doc-table")

    # Locate all anchor tags within the table
    anchor_elements = page.locator("div.table-responsive#doc-table a")
    count = anchor_elements.count()
    print(f"Found {count} anchor tags in the table.")

    # Click each anchor tag sequentially
    for i in range(count):
        href = anchor_elements.nth(i).get_attribute("href")
        print(f"Clicking on: {href}")
        anchor_elements.nth(i).click()

        download_pdf_causelist(page)
        # Wait for navigation or content to load
        page.wait_for_load_state("domcontentloaded")

        # Navigate back to the table
        page.go_back()
        page.wait_for_selector("div.table-responsive#doc-table")  

def download_pdf_causelist(page):
    try:
        # Wait for the dropdown button and click it
        page.wait_for_selector("//button[contains(@class, 'btn-primary dropdown-toggle')]", timeout=60000)
        page.click("//button[contains(@class, 'btn-primary dropdown-toggle')]")
        
        # Wait for the "Download PDF" option and click it
        page.wait_for_selector("//a[normalize-space()='Download PDF']", timeout=60000)
        page.click("//a[normalize-space()='Download PDF']")
        print("PDF download triggered successfully.")

        # Wait for the download to complete and save it to the specified folder
        with page.expect_download() as download_info:
            download = download_info.value
            download_path = download.path()  # Get the path where the file is saved

            # Move the file to the causelists folder
            download.save_as(downloads_folder / download.suggested_filename)  # Save to downloads folder
            print(f"Download saved to: {downloads_folder / download.suggested_filename}")

    except Exception as e:
        print(f"Error in downloading PDF: {e}")

if __name__ == "__main__":
    main()
