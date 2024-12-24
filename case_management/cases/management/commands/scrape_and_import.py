import os
import sys
from django.core.management.base import BaseCommand
from scripts.scrapper import main
from scripts.pdf_extractor import extract_cases
from cases.models import Judge, CaseType, Case

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class Command(BaseCommand):
    help = "Scrape case lists and import data into the database"

    def handle(self, *args, **kwargs):
        # Define the downloads folder
        downloads_folder = os.path.expanduser("~/Documents/causelists")
        os.makedirs(downloads_folder, exist_ok=True)

        # Run the Playwright scraper
        main()

        # Process the downloaded PDFs
        for filename in os.listdir(downloads_folder):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(downloads_folder, filename)
                case_data = extract_cases(pdf_path)

                print(f"The case data is {case_data}")

                # Save data to the database
                self.save_cases_to_db(case_data)

    def save_cases_to_db(self, case_data):
        for date, schedules in case_data.items():
            for schedule in schedules:
                judge, _ = Judge.objects.get_or_create(name=schedule['judge'])
                case_type, _ = CaseType.objects.get_or_create(name=schedule['case_type'])

                for case_info in schedule['cases']:
                    case_date = date
                    time = schedule['time']
                    Case.objects.get_or_create(
                        case_number=case_info['case_number'],
                        defaults={
                            'parties': case_info['parties'],
                            'date': case_date,
                            'time': time,
                            'judge': judge,
                            'case_type': case_type,
                            'meeting_link': schedule.get('meeting_link')
                        }
                    )
