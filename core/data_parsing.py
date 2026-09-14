from google import genai
from google.genai import types
from pydantic import BaseModel, Field

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
