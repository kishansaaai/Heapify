import asyncio
import json

from agents import Agent, Runner, function_tool

from heapify import Heapify

from mock_data import CALENDAR, EMAILS, NOTION_PAGES, SEARCH_RESULTS

heapify = Heapify()


# --- Query tools (reads) ---


@function_tool
@heapify.query
def search_emails(folder: str = "inbox") -> str:
    """Search emails in the given folder (inbox or sent). Returns a list of emails."""
    emails = EMAILS.get(folder, [])
    return json.dumps(emails)


@function_tool
@heapify.query
def get_calendar(date: str = "") -> str:
    """Get calendar events, optionally filtered by date (YYYY-MM-DD). Returns a list of events."""
    if date:
        events = [e for e in CALENDAR if e["date"] == date]
    else:
        events = CALENDAR
    return json.dumps(events)


@function_tool
@heapify.query
def read_notion_page(page_slug: str) -> str:
    """Read a Notion page by its slug (e.g. 'meeting-notes', 'todo-list', 'project-plan')."""
    page = NOTION_PAGES.get(page_slug)
    if page is None:
        return json.dumps({"error": f"Page '{page_slug}' not found"})
    return json.dumps(page)


@function_tool
@heapify.query
def search_internet(query: str) -> str:
    """Search the internet for information. Returns a list of search results."""
    return json.dumps(SEARCH_RESULTS["default"])


# --- Mutation tools (writes) ---


@function_tool
@heapify.mutation
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified recipient."""
    email = {"to": to, "subject": subject, "body": body, "status": "sent"}
    return json.dumps(email)


@function_tool
@heapify.mutation
def create_calendar_event(title: str, date: str, time: str, duration: int = 60, location: str = "") -> str:
    """Create a new calendar event. Date format: YYYY-MM-DD, time format: HH:MM."""
    event = {"title": title, "date": date, "time": time, "duration": duration, "location": location, "status": "created"}
    return json.dumps(event)


@function_tool
@heapify.mutation
def update_notion_page(page_slug: str, new_content: str) -> str:
    """Update a Notion page's content by its slug."""
    if page_slug not in NOTION_PAGES:
        return json.dumps({"error": f"Page '{page_slug}' not found"})
    return json.dumps({"page": page_slug, "status": "updated"})


# --- Agent ---

agent = Agent(
    name="PA Agent",
    instructions=(
        "You are a personal assistant. You help the user manage their emails, "
        "calendar, Notion documents, and search the internet. "
        "Always check existing data before taking actions. "
        "When asked to do something, confirm what you did."
    ),
    tools=[
        search_emails,
        get_calendar,
        read_notion_page,
        search_internet,
        send_email,
        create_calendar_event,
        update_notion_page,
    ],
)


async def main():
    heapify.init()

    with heapify.session() as session:
        hypothesis = heapify.hypothesize()
        print(f"Hypothesis: {hypothesis}\n")

        task = heapify.get_input()
        print(f"Task: {task}\n")

        result = await Runner.run(agent, task)
        print(f"Agent output: {result.final_output}\n")

        evaluation = heapify.evaluate(result.final_output)
        print(f"Evaluation: {evaluation}")


if __name__ == "__main__":
    asyncio.run(main())
