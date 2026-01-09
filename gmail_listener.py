import os
import base64
import time
from pathlib import Path
from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

from app.event_model import Event
from app.orchestrator import select_workflow, execute_workflow


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
ATTACH_DIR = Path("watch/email_attachments")
ATTACH_DIR.mkdir(parents=True, exist_ok=True)


def get_gmail_service():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)


def process_unread_emails():
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"]
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return

    for msg in messages:
        msg_id = msg["id"]
        message = service.users().messages().get(
            userId="me", id=msg_id
        ).execute()

        payload = message["payload"]
        parts = payload.get("parts", [])

        for part in parts:
            filename = part.get("filename")

            if filename and filename.lower().endswith(".csv"):
                att_id = part["body"]["attachmentId"]
                att = service.users().messages().attachments().get(
                    userId="me",
                    messageId=msg_id,
                    id=att_id
                ).execute()

                data = base64.urlsafe_b64decode(att["data"])
                file_path = ATTACH_DIR / filename

                with open(file_path, "wb") as f:
                    f.write(data)

                print(f"\n CSV attachment saved: {filename}", flush=True)

                event = Event(
                    event_type="DOCUMENT_RECEIVED",
                    source="email",
                    payload={
                        "filename": filename,
                        "path": str(file_path),
                        "file_type": "csv",
                        "received_at": datetime.utcnow().isoformat()
                    }
                )

                workflow = select_workflow(event)
                if workflow:
                    execute_workflow(workflow, event)

        # Mark email as read
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()


def start_gmail_listener():
    print(" Gmail listener started (polling every 30s)", flush=True)

    while True:
        process_unread_emails()
        time.sleep(30)


if __name__ == "__main__":
    start_gmail_listener()
