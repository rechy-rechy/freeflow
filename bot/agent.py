import anthropic
from anthropic import beta_tool

from bot.canvas_client import CanvasClient
from bot.google_client import GoogleClient
from bot.browser import BrowserClient
from bot.config import Config

_canvas_client: CanvasClient | None = None
_google_client: GoogleClient | None = None


def _canvas() -> CanvasClient:
    global _canvas_client
    if _canvas_client is None:
        _canvas_client = CanvasClient()
    return _canvas_client


def _google() -> GoogleClient:
    global _google_client
    if _google_client is None:
        _google_client = GoogleClient()
    return _google_client


def _browser() -> BrowserClient:
    return BrowserClient.get_instance(headless=False)


# ── Canvas tools ──────────────────────────────────────────────────────────────

@beta_tool
def list_courses(active_only: bool = True) -> str:
    """List all enrolled Canvas courses.

    Args:
        active_only: If True, only return currently active courses.
    """
    return _canvas().list_courses(active_only=active_only)


@beta_tool
def list_assignments(course_id: int, bucket: str = "upcoming") -> str:
    """List assignments for a Canvas course.

    Args:
        course_id: The numeric Canvas course ID.
        bucket: Filter by status — 'upcoming', 'past', 'undated', 'ungraded', or 'unsubmitted'.
    """
    return _canvas().list_assignments(course_id=course_id, bucket=bucket)


@beta_tool
def get_assignment(course_id: int, assignment_id: int) -> str:
    """Get full details for a specific Canvas assignment.

    Args:
        course_id: The numeric Canvas course ID.
        assignment_id: The numeric assignment ID.
    """
    return _canvas().get_assignment(course_id=course_id, assignment_id=assignment_id)


@beta_tool
def submit_assignment(
    course_id: int,
    assignment_id: int,
    submission_type: str,
    body: str = None,
    url: str = None,
) -> str:
    """Submit an assignment on Canvas.

    Args:
        course_id: The numeric Canvas course ID.
        assignment_id: The numeric assignment ID.
        submission_type: One of 'online_text_entry', 'online_url', 'online_upload'.
        body: The text body for 'online_text_entry' submissions (HTML supported).
        url: The URL for 'online_url' submissions.
    """
    return _canvas().submit_assignment(
        course_id=course_id,
        assignment_id=assignment_id,
        submission_type=submission_type,
        body=body,
        url=url,
    )


@beta_tool
def get_grades(course_id: int) -> str:
    """Get current grades for a Canvas course.

    Args:
        course_id: The numeric Canvas course ID.
    """
    return _canvas().get_grades(course_id=course_id)


@beta_tool
def get_announcements(course_id: int, count: int = 5) -> str:
    """Get recent announcements from a Canvas course.

    Args:
        course_id: The numeric Canvas course ID.
        count: Maximum number of announcements to return.
    """
    return _canvas().get_announcements(course_id=course_id, count=count)


# ── Google Docs tools ─────────────────────────────────────────────────────────

@beta_tool
def create_doc(title: str) -> str:
    """Create a new Google Doc.

    Args:
        title: The title of the new document.
    """
    return _google().create_doc(title=title)


@beta_tool
def update_doc(doc_id: str, content: str, append: bool = False) -> str:
    """Write or append content to a Google Doc.

    Args:
        doc_id: The Google Doc document ID.
        content: The text content to write.
        append: If True, append to the end; if False, replace all existing content.
    """
    return _google().update_doc(doc_id=doc_id, content=content, append=append)


@beta_tool
def get_doc(doc_id: str) -> str:
    """Read the full text content of a Google Doc.

    Args:
        doc_id: The Google Doc document ID.
    """
    return _google().get_doc(doc_id=doc_id)


@beta_tool
def list_docs(query: str = "", max_results: int = 10) -> str:
    """List Google Docs in Drive, optionally filtered by name.

    Args:
        query: Optional search string to filter by document name.
        max_results: Maximum number of documents to return.
    """
    return _google().list_docs(query=query, max_results=max_results)


# ── Gmail tools ───────────────────────────────────────────────────────────────

@beta_tool
def send_email(to: str, subject: str, body: str, html: bool = False) -> str:
    """Send an email via Gmail.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body text (plain text or HTML).
        html: If True, send as HTML; otherwise plain text.
    """
    return _google().send_email(to=to, subject=subject, body=body, html=html)


@beta_tool
def list_emails(query: str = "", max_results: int = 10) -> str:
    """List emails from Gmail inbox.

    Args:
        query: Gmail search query (e.g., 'from:teacher@school.edu', 'subject:assignment').
        max_results: Maximum number of emails to return.
    """
    return _google().list_emails(query=query, max_results=max_results)


@beta_tool
def get_email(message_id: str) -> str:
    """Get the full content of an email by ID.

    Args:
        message_id: The Gmail message ID.
    """
    return _google().get_email(message_id=message_id)


@beta_tool
def reply_to_email(message_id: str, body: str) -> str:
    """Reply to an email in the same thread.

    Args:
        message_id: The Gmail message ID to reply to.
        body: The reply text body.
    """
    return _google().reply_to_email(message_id=message_id, body=body)


# ── Browser automation tools ──────────────────────────────────────────────────

@beta_tool
def browser_navigate(url: str) -> str:
    """Open a URL in the browser. Use this for portals without a direct API.

    Args:
        url: The full URL to navigate to.
    """
    return _browser().navigate(url=url)


@beta_tool
def browser_get_text(selector: str = "body") -> str:
    """Extract text from the current browser page.

    Args:
        selector: CSS selector of the element to extract text from. Defaults to entire page body.
    """
    return _browser().get_text(selector=selector)


@beta_tool
def browser_click(selector: str) -> str:
    """Click an element on the current browser page.

    Args:
        selector: CSS selector of the element to click.
    """
    return _browser().click(selector=selector)


@beta_tool
def browser_fill(selector: str, value: str) -> str:
    """Fill a form field on the current browser page.

    Args:
        selector: CSS selector of the input field.
        value: The value to type into the field.
    """
    return _browser().fill(selector=selector, value=value)


@beta_tool
def browser_screenshot(path: str = "/tmp/screenshot.png") -> str:
    """Take a screenshot of the current browser page for debugging.

    Args:
        path: File path where the screenshot will be saved.
    """
    return _browser().screenshot(path=path)


ALL_TOOLS = [
    list_courses,
    list_assignments,
    get_assignment,
    submit_assignment,
    get_grades,
    get_announcements,
    create_doc,
    update_doc,
    get_doc,
    list_docs,
    send_email,
    list_emails,
    get_email,
    reply_to_email,
    browser_navigate,
    browser_get_text,
    browser_click,
    browser_fill,
    browser_screenshot,
]

SYSTEM_PROMPT = f"""You are a school automation assistant helping a student manage their academic life.
You have access to tools for Canvas LMS, Google Docs/Drive/Gmail, and browser automation.

The student's school email is: {Config.SCHOOL_EMAIL}

Guidelines:
- Always confirm before submitting assignments — this is irreversible.
- When looking up courses or assignments, list them first so the student can confirm which one.
- For emails to teachers, draft the message and ask for approval before sending.
- Use the Canvas API tools first; fall back to browser automation only if the API can't accomplish the task.
- Be concise and clear in your responses. Format lists and data readably.
- If a task requires multiple steps, explain what you're doing at each step.
"""


class SchoolAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.history: list[dict] = []

    def chat(self, user_message: str) -> str:
        messages = self.history + [{"role": "user", "content": user_message}]
        runner = self.client.beta.messages.tool_runner(
            model="claude-opus-4-7",
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"effort": "xhigh"},
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=messages,
        )
        final_text = ""
        for message in runner:
            for block in message.content:
                if hasattr(block, "type") and block.type == "text":
                    final_text = block.text

        self.history.append({"role": "user", "content": user_message})
        if final_text:
            self.history.append({"role": "assistant", "content": final_text})
        return final_text or "No response generated."
