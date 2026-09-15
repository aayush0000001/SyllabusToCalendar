from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import date ,timedelta
from pathlib import Path

CREDENTIALS_FILE = Path(__file__).resolve().parent /"credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

#runs Oauth flow
def get_calendar_service():

    #loads client config such as client id and client secret from credentials file, this initializes Oauth flow object with specified scopes
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)

    #launches a temporary webserver to run default web browser and run google login and consent screen which captures authentication to create active access credentials(creds)
    creds = flow.run_local_server(port=0)

    #returns googleapi for the specified user using their creds
    return build("calendar", "v3", credentials=creds)

#building event body
def build_event_body(title: str, event_date:str):

    #setting start date and adding 1 day timedelta for end date for the event
    start=date.fromisoformat(event_date)
    end=start+timedelta(days=1)

    #returning the event title as summary and the start and end date in specified timezone
    return{
        "summary": title,
        "start": {"date":start.isoformat(),},
        "end":{"date":end.isoformat(),},
    }
def upload_to_calendar(parsed_data: str):

    #initializing Oauth flow
    service = get_calendar_service()

    #looping through each event to create it
    for event in parsed_data.get("events",[]):
        title=event["title"]
        event_date=event["event_date"]

        #building a all-day event payload
        body= build_event_body(title, event_date)

        #sending request through Google Calendar API
        created_event= service.events().insert(
            calendarId='primary',
            body=body,
        ).execute()

        print(f"Added: {title} {event_date}")