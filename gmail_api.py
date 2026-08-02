import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Read-only scope (safest)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service():
    """Authenticate and return Gmail service object."""
    creds = None
    
    # Check if we already have a saved token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def fetch_recent_emails(max_results=5):
    """Fetch recent emails from Gmail inbox."""
    service = get_gmail_service()
    
    # Get message list
    results = service.users().messages().list(
        userId='me',
        maxResults=max_results,
        labelIds=['INBOX']
    ).execute()
    
    messages = results.get('messages', [])
    emails = []
    
    for msg in messages:
        # Get full message
        full_msg = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        
        # Extract headers
        headers = full_msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        
        # Extract body snippet
        snippet = full_msg.get('snippet', '')
        
        emails.append({
            "from": sender,
            "subject": subject,
            "body": snippet
        })
    
    return emails


# ===== TEST =====
if __name__ == "__main__":
    print("📧 Fetching recent Gmail emails...")
    print("⚠️  Browser will open — approve access!\n")
    
    emails = fetch_recent_emails(max_results=3)
    
    print(f"✅ Found {len(emails)} emails:\n")
    for i, email in enumerate(emails, 1):
        print(f"[Email {i}]")
        print(f"From:    {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Preview: {email['body'][:150]}...")
        print()