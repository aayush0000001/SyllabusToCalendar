import json
from pathlib import Path
from core.data_extraction import syllabus_ingestion
from core.data_parsing import extracted_data_parsing
from core.calendar_integration import upload_to_calendar


def main():

    #getting directory of current script
    HERE = Path(__file__).resolve().parent

    #variable to store pdf address
    syllabus=HERE/ "CSCI2073.pdf"

    #variable to store term year
    class_year=2026

    #converting extracted list into string for gemini prompting
    extracted_text=str(syllabus_ingestion(syllabus))

    #printing extracted text to see if its being properly setup or no
    with open("raw_output.txt","w") as file1:
        file1.write(extracted_text)

    #storing parsed data(json string) as dictionary
    parsed_data = json.loads(extracted_data_parsing(extracted_text,class_year))

    #printing extracted_data_parsing to see if our data is parsed like we want it to be
    with open("output.txt", "w") as file:
        json.dump(parsed_data, file)


    upload_to_calendar(parsed_data)


main()