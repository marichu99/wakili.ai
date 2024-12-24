import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
from PyPDF2 import PdfReader
from cases.models import Judge, CaseType, Case
import django

# Initialize Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "case_management.settings")
django.setup()

def main():
    # Define the downloads folder path
    downloads_folder = Path.home() / "Documents" / "causelists"
    downloads_folder.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )

        page = context.new_page()
        page.goto("https://kenyalaw.org/kenyalawblog/introducing-the-new-kenya-law-website/", timeout=60000)

        # Ensure the page is fully loaded
        page.wait_for_load_state("networkidle")
        scroll_through_page(page)

        # Save the initial page content
        html_content = page.content()
        with open("kenyalaw.html", "w+", encoding="utf8") as kFile:
            kFile.write(html_content)

        time.sleep(6)
        # Get Cause List
        get_cause_list_all(page, downloads_folder)

        # Close the browser
        browser.close()

def scroll_through_page(page):
    page.evaluate("""() => {
        window.scrollTo(0, document.body.scrollHeight);
    }""")
    time.sleep(2)

def get_cause_list_all(page, downloads_folder):
    try:
        # Click the 'Cause List' link
        page.click("//a[normalize-space()='Cause List']")
        page.wait_for_selector("div.flow-columns.mb-3 a")

        # Locate all anchor tags inside the specific div
        anchor_elements = page.locator("div.flow-columns.mb-3 a")
        count = anchor_elements.count()
        print(f"Found {count} anchor tags inside the div.")

        # Click each anchor tag sequentially
        for i in range(count):
            href = anchor_elements.nth(i).get_attribute("href")
            print(f"Clicking on: {href}")
            anchor_elements.nth(i).click()
            page.wait_for_selector("//label[normalize-space()='Monthly Cause List']")

            # Filter cause list content
            page.click("//label[normalize-space()='Monthly Cause List']")
            
            click_table_anchors(page, downloads_folder)

            page.go_back()
            page.wait_for_selector("div.flow-columns.mb-3 a")

    except Exception as e:
        print("Error getting the cause list:", str(e))

def click_table_anchors(page, downloads_folder):
    page.wait_for_selector("div.table-responsive#doc-table")
    anchor_elements = page.locator("div.table-responsive#doc-table a")
    count = anchor_elements.count()
    print(f"Found {count} anchor tags in the table.")

    for i in range(count):
        href = anchor_elements.nth(i).get_attribute("href")
        print(f"Clicking on: {href}")
        anchor_elements.nth(i).click()

        download_pdf_causelist(page, downloads_folder)
        page.wait_for_load_state("domcontentloaded")
        page.go_back()
        page.wait_for_selector("div.table-responsive#doc-table")

def download_pdf_causelist(page, downloads_folder):
    try:
        page.wait_for_selector("//button[contains(@class, 'btn-primary dropdown-toggle')]", timeout=60000)
        page.click("//button[contains(@class, 'btn-primary dropdown-toggle')]")
        page.wait_for_selector("//a[normalize-space()='Download PDF']", timeout=60000)
        
        # Handle download
        with page.expect_download() as download_info:
            page.click("//a[normalize-space()='Download PDF']")
        download = download_info.value
        file_path = downloads_folder / download.suggested_filename
        download.save_as(file_path)
        print(f"Download saved to: {file_path}")
    except Exception as e:
        print(f"Error in downloading PDF: {e}")

if __name__ == "__main__":
    main()
