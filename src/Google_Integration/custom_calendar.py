import datetime
import pickle
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleCalendar:
    # Define the scopes required for Google Calendar API access
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

    # Path to the credentials file obtained from the Google Cloud Console
    CREDENTIALS_FILE = 'credentials.json'

    def __init__(self):
        """
        Initializes the GoogleCalendar instance, attempting to authenticate with Google's API.
        """
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """
        Authenticates the user using the credentials file and saves the credentials for future use.
        If existing credentials are invalid or expired, it performs a new login flow, make sure to delete the token.pickle file.
        """
        token_pickle = 'token.pickle'
        if os.path.exists(token_pickle):
            with open(token_pickle, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(token_pickle, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_events_for_today(self):
        """
        Fetches and prints the calendar events for the current day.
        :return: A list of events happening today.
        """
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        end = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + 'Z'
        print('Getting the upcoming events')
        events_result = self.service.events().list(calendarId='primary', timeMin=now, timeMax=end, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

        return events

    def add_event_to_calendar(self, summary, start_time, end_time, description='', location=''):
        """
        Adds an event to the Google Calendar.
        :param summary: The summary or title of the event.
        :param start_time: The start time of the event in RFC3339 format.
        :param end_time: The end time of the event in RFC3339 format.
        :param description: The description of the event (optional).
        :param location: The location of the event (optional).
        :return: The created event object from the API response.
        """
        event_body = {
            'summary': summary,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
            'description': description,
            'location': location,
        }

        created_event = self.service.events().insert(calendarId='primary', body=event_body).execute()
        print(f"Created event id: {created_event.get('id')}")
        return created_event

# Usage example
if __name__ == '__main__':
    calendar = GoogleCalendar()
    events_today = calendar.get_events_for_today()
    print(f"Events today: {events_today}")

