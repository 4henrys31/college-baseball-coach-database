import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

print("Starting Google Sheets diagnostic test...")

spreadsheet_id = os.getenv("SPREADSHEET_ID")
service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

if not spreadsheet_id:
    raise ValueError("Missing SPREADSHEET_ID secret.")

if not service_account_json:
    raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT_JSON secret.")

print("SPREADSHEET_ID found.")
print(f"SPREADSHEET_ID starts with: {spreadsheet_id[:8]}...")

try:
    creds_dict = json.loads(service_account_json)
    print("Service account JSON loaded successfully.")
    print(f"Service account email: {creds_dict.get('client_email')}")
except Exception as e:
    raise ValueError(f"Could not parse GOOGLE_SERVICE_ACCOUNT_JSON: {e}")

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

try:
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    print("Google authorization successful.")
except Exception as e:
    raise RuntimeError(f"Google authorization failed: {e}")

try:
    spreadsheet = client.open_by_key(spreadsheet_id)
    print(f"Opened spreadsheet successfully: {spreadsheet.title}")
except Exception as e:
    raise RuntimeError(f"Could not open spreadsheet. Check Sheet ID and sharing permissions: {e}")

try:
    worksheets = spreadsheet.worksheets()
    print("Existing worksheet tabs:")
    for ws in worksheets:
        print(f"- {ws.title}")
except Exception as e:
    raise RuntimeError(f"Could not list worksheets: {e}")

test_tab_name = "Connection Test"

try:
    try:
        worksheet = spreadsheet.worksheet(test_tab_name)
        print("Connection Test tab already exists.")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=test_tab_name, rows=100, cols=10)
        print("Connection Test tab created.")

    worksheet.clear()
    worksheet.update(
        "A1:D2",
        [
            ["Status", "Timestamp", "Spreadsheet Title", "Message"],
            [
                "SUCCESS",
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                spreadsheet.title,
                "GitHub Actions successfully wrote to Google Sheets.",
            ],
        ],
    )

    print("Diagnostic write completed successfully.")

except Exception as e:
    raise RuntimeError(f"Could not write to spreadsheet: {e}")
