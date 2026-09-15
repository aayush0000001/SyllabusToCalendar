from typing import List, Dict, Any
import re
import pdfplumber


#defining a function for syllabus data extraction and storing the data extracted into a dictionary.
def syllabus_ingestion(syllabus: str) -> List[Dict[str,Any]]:

    #list that stores extracted records`        `
    extracted_records=[]

    #regex pattern to filter potential schedule texts
    schedule_pattern =re.compile(
            r"\b(?:\d{1,2}[/-]\d{1,2}|"
            r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
            r"due|exam|homework)",
            re.IGNORECASE,
        )


    #opening the syllabus pdf with pdf plumber to read from it
    with pdfplumber.open(syllabus) as pdf:

        #reading with page indexing
        for page_num, page in enumerate(pdf.pages):

            #scanning and reading for tables in the pdf
            tables=page.extract_tables()

            if tables:

                #reading table if found with row indexing
                for table_index, table in enumerate(tables):

                    for row  in table:

                        #strip any unnecessary whitespace in any particular cell + replace an empty cell with an empty string
                        cleaned_row=[cell.strip() if cell else "" for cell in row]

                        #filtering rows that contain actual data and appending to extracted records list with relevant data
                        if any(cleaned_row):

                            #converting cleaned row list into string
                            row_text=" ".join(cleaned_row)

                            #comparing rowtexts with the regex pattern for possible schedules to make sure we only store potential schedules
                            if schedule_pattern.search(row_text):

                                extracted_records.append({
                                    "page":page_num,
                                    "type":"table_row",
                                    "source_index":table_index,
                                    "content": cleaned_row
                                })

            else:

                            #read text if there are no tables in the current page
                            text=page.extract_text()


                            if text:

                                #reading text if text found, stripping each line and reading for data
                                lines = text.split("\n")

                                for line in lines:

                                    cleaned_line=line.strip()

                                    #if there is a cleaned line then append the data in the line to extracted_records list.
                                    if cleaned_line:
                                        extracted_records.append({
                                            "page":page_num,
                                            "type":"text_line",
                                            "source_index": None,
                                            "content": cleaned_line
                                        })
    return extracted_records
