from typing import List, Dict, Any
import json
import re
import pdfplumber
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


def main():

    #variable to store pdf address
    syllabus="CSCI2073.pdf"

    #converting extracted list into string for gemini prompting
    extracted_text=str(syllabus_ingestion(syllabus))

    #printing extracted text to see if its being properly setup or no
    with open("raw_output.txt","w") as file1:
        file1.write(extracted_text)

    #printing extracted_data_parsing to see if our data is parsed like we want it to be
    with open("output.txt", "w") as file:
        json.dump(extracted_data_parsing(extracted_text), file)


def extracted_data_parsing(extracted_text):
    # loading gemini api through environment variable
    client=genai.Client()

    #defining blueprint for an individual event from syllabus
    class event(BaseModel):

        title: str= Field(description="Name of the event")
        event_date: str= Field(description="ISO-8601 format date")

    #defining wrapper for all events from syllabus for structured data receiving
    class SyllabusSchedule(BaseModel):
        events:list[event]

    #text processing function
    def parse_syllabus(extracted_text):
        response=client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents="extract all dates paired with event names for this data:"+extracted_text,
            config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SyllabusSchedule,
            temperature=0.1),
        )
        return response.text
    return parse_syllabus(extracted_text)


#defining a function for syllabus data extraction and storing the data extracted into a dictionary.
def syllabus_ingestion(syllabus: str) -> List[Dict[str,Any]]:

    #list that stores extracted records
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
main()