# Calendar Chatbot

A simple command-line chatbot to interact with your Google Calendar.  
You can view, add, and delete events using natural language commands.

## Features

- View today's, tomorrow's, or next month's events
- Add events with natural language (e.g., "Add a doctor appointment on 2025-08-10 at 3 PM")
- Delete a specific event by number
- Delete all upcoming events

## Setup

1. **Clone this repository** and navigate to the project folder.

2. **Install dependencies:**
    ```sh
    pip install google-auth google-auth-oauthlib google-api-python-client dateparser
    ```

3. **Google Calendar API Setup:**
    - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
    - Create a project and enable the Google Calendar API.
    - Create OAuth client credentials for a Desktop app.
    - Download `credentials.json` and place it in the project folder.

4. **First Run:**
    - On first run, you will be prompted to authenticate with your Google account in a browser.

## Usage

Run the chatbot:

```sh
python chatbot.py
```

You can ask:

- `What's on my calendar today?`
- `What's on my calendar tomorrow?`
- `What's on my calendar for next month?`
- `Add a meeting with John tomorrow at 3 PM`
- `Add a doctor appointment on 2025-08-10 at 3 PM`
- `Delete event number 2`
- `Delete all`
- `Exit`

## Example

```
You: What's on my calendar today?
Bot: Today's events:
- Meeting with John at 2025-08-10T15:00:00+05:30

You: Add a doctor appointment on 2025-08-10 at 3 PM
Bot: ✅ Event created: <Google Calendar link>

You: Delete event number 2
Bot: 🗑️ Event deleted successfully.

You: Delete all
Bot: ⚠️ Delete ALL upcoming events? Type 'yes' to confirm: yes
Bot: ✅ All upcoming events deleted.
```
