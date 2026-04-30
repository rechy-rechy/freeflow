import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from bot.config import Config

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GoogleClient:
    def __init__(self):
        creds = self._get_credentials()
        self.docs = build("docs", "v1", credentials=creds)
        self.drive = build("drive", "v3", credentials=creds)
        self.gmail = build("gmail", "v1", credentials=creds)

    def _get_credentials(self) -> Credentials:
        token_path = Path(Config.GOOGLE_TOKEN_FILE)
        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json())
        return creds

    def create_doc(self, title: str) -> str:
        try:
            doc = self.docs.documents().create(body={"title": title}).execute()
            return json.dumps({
                "doc_id": doc["documentId"],
                "title": doc["title"],
                "url": f"https://docs.google.com/document/d/{doc['documentId']}/edit",
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def update_doc(self, doc_id: str, content: str, append: bool = False) -> str:
        try:
            doc = self.docs.documents().get(documentId=doc_id).execute()
            requests = []
            if not append:
                body_content = doc.get("body", {}).get("content", [])
                end_index = body_content[-1].get("endIndex", 1) - 1 if body_content else 1
                if end_index > 1:
                    requests.append({
                        "deleteContentRange": {
                            "range": {"startIndex": 1, "endIndex": end_index}
                        }
                    })
            requests.append({
                "insertText": {
                    "location": {"index": 1},
                    "text": content,
                }
            })
            self.docs.documents().batchUpdate(
                documentId=doc_id, body={"requests": requests}
            ).execute()
            return json.dumps({"success": True, "doc_id": doc_id})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_doc(self, doc_id: str) -> str:
        try:
            doc = self.docs.documents().get(documentId=doc_id).execute()
            text_parts = []
            for element in doc.get("body", {}).get("content", []):
                paragraph = element.get("paragraph")
                if paragraph:
                    for pe in paragraph.get("elements", []):
                        text_run = pe.get("textRun")
                        if text_run:
                            text_parts.append(text_run.get("content", ""))
            return json.dumps({
                "doc_id": doc_id,
                "title": doc.get("title", ""),
                "content": "".join(text_parts),
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_docs(self, query: str = "", max_results: int = 10) -> str:
        try:
            q = "mimeType='application/vnd.google-apps.document'"
            if query:
                q += f" and name contains '{query}'"
            result = self.drive.files().list(
                q=q,
                pageSize=max_results,
                fields="files(id, name, modifiedTime, webViewLink)",
                orderBy="modifiedTime desc",
            ).execute()
            files = result.get("files", [])
            return json.dumps([{
                "doc_id": f["id"],
                "name": f["name"],
                "modified": f.get("modifiedTime"),
                "url": f.get("webViewLink"),
            } for f in files])
        except Exception as e:
            return json.dumps({"error": str(e)})

    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> str:
        try:
            if html:
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(body, "html"))
            else:
                msg = MIMEText(body)
            msg["to"] = to
            msg["from"] = Config.SCHOOL_EMAIL
            msg["subject"] = subject
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            sent = self.gmail.users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()
            return json.dumps({"success": True, "message_id": sent["id"]})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_emails(self, query: str = "", max_results: int = 10) -> str:
        try:
            result = self.gmail.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()
            messages = result.get("messages", [])
            emails = []
            for m in messages:
                msg = self.gmail.users().messages().get(
                    userId="me", id=m["id"], format="metadata",
                    metadataHeaders=["From", "To", "Subject", "Date"]
                ).execute()
                headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
                emails.append({
                    "id": m["id"],
                    "from": headers.get("From", ""),
                    "to": headers.get("To", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": msg.get("snippet", ""),
                })
            return json.dumps(emails)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_email(self, message_id: str) -> str:
        try:
            msg = self.gmail.users().messages().get(
                userId="me", id=message_id, format="full"
            ).execute()
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            body = self._extract_body(msg.get("payload", {}))
            return json.dumps({
                "id": message_id,
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "body": body,
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def reply_to_email(self, message_id: str, body: str) -> str:
        try:
            original = self.gmail.users().messages().get(
                userId="me", id=message_id, format="metadata",
                metadataHeaders=["From", "Subject", "Message-ID", "References"]
            ).execute()
            headers = {h["name"]: h["value"] for h in original.get("payload", {}).get("headers", [])}
            thread_id = original.get("threadId")

            msg = MIMEText(body)
            msg["to"] = headers.get("From", "")
            msg["from"] = Config.SCHOOL_EMAIL
            msg["subject"] = f"Re: {headers.get('Subject', '')}"
            msg["In-Reply-To"] = headers.get("Message-ID", "")
            references = headers.get("References", "")
            msg_id = headers.get("Message-ID", "")
            msg["References"] = f"{references} {msg_id}".strip()

            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            sent = self.gmail.users().messages().send(
                userId="me", body={"raw": raw, "threadId": thread_id}
            ).execute()
            return json.dumps({"success": True, "message_id": sent["id"]})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _extract_body(self, payload: dict) -> str:
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        for part in payload.get("parts", []):
            result = self._extract_body(part)
            if result:
                return result
        return ""
