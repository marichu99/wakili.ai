import re
from PyPDF2 import PdfReader

def extract_cases(pdf_path):
    # Initialize the extracted data structure
    data = {}
    
    # Load the PDF and extract text
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() for page in reader.pages)

    # Split the text into sections by date or other delimiters (e.g., "05 November 2024")
    sections = re.split(r"(\d{2} \w+ \d{4})", text)  # Matches dates like "05 November 2024"
    
    for i in range(1, len(sections), 2):  # Process dates and their corresponding content
        date = sections[i].strip()
        content = sections[i + 1]

        # Split content into lines for detailed parsing
        lines = content.splitlines()

        current_schedule = {
            "time": None,
            "judge": None,
            "case_type": None,
            "cases": [],
            "meeting_link": None
        }

        for line in lines:
            # Extract time (e.g., "09:00 AM")
            if re.search(r"\b\d{1,2}:\d{2} (AM|PM)\b", line):
                current_schedule["time"] = line.strip()
            
            # Extract judge information
            elif "HON." in line:
                current_schedule["judge"] = line.strip()
            
            # Extract case type
            elif line.upper() in [
                "MENTION", "HEARING", "JUDGMENT", "FRESH HEARING", "DEFENSE HEARING",
                "DIRECTIONS", "HEARING OF APPLICATIONS"
            ]:
                current_schedule["case_type"] = line.strip()
            
            # Extract cases (e.g., "HC.CR.C/7/2019 The Republic Vs Abisaye Odongo")
            elif "Vs" in line or "VS" in line:
                parts = line.split(maxsplit=1)
                if len(parts) > 1:
                    case_number = parts[0]
                    parties = parts[1]
                    current_schedule["cases"].append({
                        "case_number": case_number,
                        "parties": parties
                    })
            
            # Extract online meeting link (e.g., Zoom or Teams link)
            elif re.search(r"https?://\S+", line):
                current_schedule["meeting_link"] = line.strip()

        # Add extracted information to the data structure
        if current_schedule["time"] and current_schedule["cases"]:
            if date not in data:
                data[date] = []
            data[date].append(current_schedule)

    return data
