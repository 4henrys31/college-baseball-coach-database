import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .config import settings
from .schema import COACH_COLUMNS, VALIDATION_COLUMNS, CHANGELOG_COLUMNS, TABS, DIVISION_TABS

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def service():
    creds = Credentials.from_service_account_file(settings.google_service_account_file, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)


def ensure_tabs():
    svc = service()
    meta = svc.spreadsheets().get(spreadsheetId=settings.spreadsheet_id).execute()
    existing = {s['properties']['title'] for s in meta.get('sheets', [])}
    requests = []
    for title in TABS:
        if title not in existing:
            requests.append({'addSheet': {'properties': {'title': title}}})
    if requests:
        svc.spreadsheets().batchUpdate(spreadsheetId=settings.spreadsheet_id, body={'requests': requests}).execute()


def clear_and_write(tab: str, columns: list[str], rows: list[dict]):
    svc = service()
    values = [columns] + [[r.get(c, '') for c in columns] for r in rows]
    svc.spreadsheets().values().clear(spreadsheetId=settings.spreadsheet_id, range=f"'{tab}'!A:ZZ").execute()
    if values:
        svc.spreadsheets().values().update(
            spreadsheetId=settings.spreadsheet_id,
            range=f"'{tab}'!A1",
            valueInputOption='RAW',
            body={'values': values}
        ).execute()


def sync_all(coach_rows: list[dict], validation_rows: list[dict] | None = None, changelog_rows: list[dict] | None = None):
    ensure_tabs()
    clear_and_write('Master Database', COACH_COLUMNS, coach_rows)
    for division, tab in DIVISION_TABS.items():
        subset = [r for r in coach_rows if r.get('division') == division]
        if subset or tab in ['NCAA Division 1','NCAA Division 2','NCAA Division 3','NAIA','Junior College / Two-Year Programs']:
            if tab == 'Junior College / Two-Year Programs':
                subset = [r for r in coach_rows if r.get('division') in ['NJCAA','CCCAA','NWAC','Junior College','Two-Year']]
            clear_and_write(tab, COACH_COLUMNS, subset)
    clear_and_write('Validation Report', VALIDATION_COLUMNS, validation_rows or [])
    clear_and_write('Annual Change Log', CHANGELOG_COLUMNS, changelog_rows or [])
    needs_review = [r for r in coach_rows if r.get('data_status') != 'Verified']
    clear_and_write('Missing / Needs Manual Review', COACH_COLUMNS, needs_review)
    clear_and_write('Outreach Tracker', COACH_COLUMNS, coach_rows)
