import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SERVICE_ACCOUNT_JSON = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds_dict = json.loads(SERVICE_ACCOUNT_JSON)
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)

sheet = client.open_by_key(SPREADSHEET_ID)

try:
    worksheet = sheet.worksheet("Master Database")
except gspread.WorksheetNotFound:
    worksheet = sheet.add_worksheet(title="Master Database", rows=1000, cols=30)

headers = [
    "Division",
    "School",
    "State",
    "Conference",
    "Coach First Name",
    "Coach Last Name",
    "Title",
    "Role Category",
    "Email",
    "Phone",
    "Athletics Website",
    "Baseball Page URL",
    "Staff Directory URL",
    "Source URL",
    "Last Verified Date",
    "Data Status",
    "Contacted?",
    "Date Contacted",
    "Contact Method",
    "Follow-Up Date",
    "Follow-Up Status",
    "Camp Invite Sent?",
    "Clinic Invite Sent?",
    "Player Interest Level",
    "Coach Response",
    "Next Action",
    "Notes",
    "Do Not Contact?"
]

worksheet.clear()
worksheet.append_row(headers)

worksheet.append_row([
    "TEST",
    "Test University",
    "TX",
    "Test Conference",
    "John",
    "Doe",
    "Head Baseball Coach",
    "Head Coach",
    "test@example.com",
    "555-555-5555",
    "https://example.com",
    "https://example.com/baseball",
    "https://example.com/staff",
    "https://example.com/source",
    datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    "Connection Test",
    "No",
    "",
    "",
    "",
    "",
    "No",
    "No",
    "",
    "",
    "",
    "Google Sheets connection test row",
    "No"
])

print("Google Sheet connection test completed successfully.")
