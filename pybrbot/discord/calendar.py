from datetime import datetime
from collections import defaultdict
import pytz
import httpx
from loguru import logger

ROOMS = [
    {
        "discord_channel": "trilha-pep{}".format(pep_number),
        "calendar_room_name": "PEP {}".format(pep_number),
    }
    for pep_number in [0, 8, 20, 404]
]


def fetch_events():
    calendar_api = (
        "https://www.googleapis.com/calendar/v3/calendars"
        "/cis4uq8vegrfbjjn1qi9hvau1k%40group.calendar.google.com/events?"
        "key=AIzaSyAIn8DyZFtthupLozgwIX3NUURFMWEIPb4&singleEvents=true"
        "&timeMin=2020-11-02T00%3A00%3A00.000Z&timeMax=2020-11-09T00%3A00%3A00.000Z"
        "&maxResults=9999&timeZone=America%2FSao_Paulo"
    )
    response = httpx.get(calendar_api)
    items = response.json()["items"]
    logger.info(f"Events found: {len(items)}")

    return sorted(items, key=lambda item: item["start"]["dateTime"])


def next_event(events, location):
    now = datetime.now(pytz.timezone("America/Sao_Paulo")).isoformat()
    for event in events:
        if event["start"]["dateTime"] < now:
            continue

        if event.get("location") == location:
            return event
