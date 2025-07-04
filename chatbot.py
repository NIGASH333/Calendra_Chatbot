import datetime
import re
import os.path
import dateparser
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def read_today_events(service):
    now = datetime.datetime.utcnow()
    end_of_day = now.replace(hour=23, minute=59, second=59)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat() + 'Z',
        timeMax=end_of_day.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    if not events:
        print("You have no events today.")
    else:
        print("Today's events:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {event['summary']} at {start}")

def read_events_for_date(service, date):
    start_of_day = datetime.datetime.combine(date, datetime.time.min)
    end_of_day = datetime.datetime.combine(date, datetime.time.max)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day.isoformat() + 'Z',
        timeMax=end_of_day.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    if not events:
        print(f"No events on {date.strftime('%Y-%m-%d')}.")
    else:
        print(f"Events on {date.strftime('%Y-%m-%d')}:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {event['summary']} at {start}")

def read_events_for_range(service, start_date, end_date):
    start = datetime.datetime.combine(start_date, datetime.time.min)
    end = datetime.datetime.combine(end_date, datetime.time.max)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    if not events:
        print(f"No events from {start_date} to {end_date}.")
    else:
        print(f"Events from {start_date} to {end_date}:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {event['summary']} at {start}")

def create_event(service, title, date_str, time_str):
    try:
        event_datetime = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        end_time = event_datetime + datetime.timedelta(hours=1)
        event = {
            'summary': title,
            'start': {'dateTime': event_datetime.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"✅ Event created: {created_event.get('htmlLink')}")
    except ValueError:
        print("Invalid date/time. Use YYYY-MM-DD and HH:MM format.")

def list_events_with_indices(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    if not events:
        print("No upcoming events found.")
        return []
    print("Upcoming events:")
    for i, event in enumerate(events, 1):
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{i}. {event['summary']} at {start}")
    return events

def delete_event(service, event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print("🗑️ Event deleted successfully.")
    except Exception as e:
        print("Error deleting event:", str(e))

def delete_all_events(service):
    confirm = input("⚠️ Delete ALL upcoming events? Type 'yes' to confirm: ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=2500,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    if not events:
        print("No upcoming events to delete.")
        return

    for event in events:
        try:
            service.events().delete(calendarId='primary', eventId=event['id']).execute()
            print(f"Deleted: {event.get('summary', 'Unnamed Event')}")
        except Exception as e:
            print("Failed:", str(e))

    print("✅ All upcoming events deleted.")

def chatbot():
    service = authenticate_google_calendar()
    print("\n👋 Hello! I'm your Calendar Chatbot.")
    print("You can ask:")
    print("➤ What's on my calendar today?")
    print("➤ What's on my calendar tomorrow?")
    print("➤ What's on my calendar for next month?")
    print("➤ Add a meeting with John tomorrow at 3 PM")
    print("➤ Add a doctor appointment on 2025-08-10 at 3 PM")
    print("➤ Delete event")
    print("➤ Exit")

    while True:
        command = input("\nYou: ").strip().lower()

        if "calendar" in command:
            if "tomorrow" in command:
                date = datetime.date.today() + datetime.timedelta(days=1)
                read_events_for_date(service, date)
            elif "today" in command:
                read_today_events(service)
            elif "next month" in command:
                today = datetime.date.today()
                first = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
                last = (first + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
                read_events_for_range(service, first, last)
            else:
                print("Try: today, tomorrow, or next month.")

        elif "add" in command and "meeting" in command:
            match = re.search(r'add a meeting with (.+?) (today|tomorrow|on \d{4}-\d{2}-\d{2}) at (\d{1,2}(:\d{2})?\s?(am|pm))', command)
            if match:
                person = match.group(1).strip()
                day = match.group(2)
                time_raw = match.group(3).replace(" ", "").upper()

                try:
                    time_obj = datetime.datetime.strptime(time_raw, "%I%p")
                except ValueError:
                    time_obj = datetime.datetime.strptime(time_raw, "%I:%M%p")
                time_str = time_obj.strftime("%H:%M")

                if day == "today":
                    date = datetime.date.today()
                elif day == "tomorrow":
                    date = datetime.date.today() + datetime.timedelta(days=1)
                else:
                    date = datetime.datetime.strptime(day[3:], "%Y-%m-%d").date()

                create_event(service, f"Meeting with {person}", date.isoformat(), time_str)
            else:
                print("Try: Add a meeting with John on 2025-08-10 at 3 PM")

        elif "add" in command:
            match = re.search(r'add (.+?) (on|at|for)? (.+)', command)
            if match:
                title = match.group(1).strip()
                datetime_text = match.group(3).strip()
                parsed_dt = dateparser.parse(datetime_text)
                if parsed_dt:
                    event_date = parsed_dt.date().isoformat()
                    event_time = parsed_dt.strftime("%H:%M")
                    create_event(service, title.title(), event_date, event_time)
                else:
                    print("Could not parse date/time.")
            else:
                print("Try: Add dentist appointment on 2025-08-10 at 11 AM")

        elif "delete all" in command:
            delete_all_events(service)

        elif "delete" in command:
            events = list_events_with_indices(service)
            if not events:
                continue
            try:
                choice = int(input("Enter event number to delete: "))
                if 1 <= choice <= len(events):
                    delete_event(service, events[choice - 1]['id'])
                else:
                    print("Invalid number.")
            except ValueError:
                print("Enter a valid number.")

        elif "exit" in command:
            print("👋 Goodbye!")
            break

        else:
            print("I didn't understand that. Try again.")

if __name__ == '__main__':
    chatbot()
