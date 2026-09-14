import json
from core.data_extraction import syllabus_ingestion
from core.data_parsing import extracted_data_parsing
from calendar_integration import upload_to_calendar


def main():

    #variable to store pdf address
    syllabus="CSCI2073.pdf"

    #converting extracted list into string for gemini prompting
    extracted_text=str(syllabus_ingestion(syllabus))

    #printing extracted text to see if its being properly setup or no
    with open("raw_output.txt","w") as file1:
        file1.write(extracted_text)

    #storing parsed data(json string) as dictionary
    parsed_data = json.loads(extracted_data_parsing(extracted_text))

    #printing extracted_data_parsing to see if our data is parsed like we want it to be
    with open("output.txt", "w") as file:
        json.dump(parsed_data, file)


    upload_to_calendar(parsed_data)


main()