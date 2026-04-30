"""One-time script to authorize Google APIs and save token.json."""
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from bot.config import Config

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def main():
    creds_file = Config.GOOGLE_CREDENTIALS_FILE
    token_file = Config.GOOGLE_TOKEN_FILE

    if not Path(creds_file).exists():
        print(f"Error: credentials file not found at '{creds_file}'")
        print("Download it from Google Cloud Console:")
        print("  1. Go to console.cloud.google.com")
        print("  2. Create a project and enable Docs, Drive, and Gmail APIs")
        print("  3. Create OAuth2 Desktop credentials and download the JSON file")
        print(f"  4. Save it as '{creds_file}'")
        return

    flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
    creds = flow.run_local_server(port=0)
    Path(token_file).write_text(creds.to_json())
    print(f"Authorization complete. Token saved to '{token_file}'")
    print("You can now run: python main.py chat")


if __name__ == "__main__":
    main()
