# College Baseball Coach Recruiting Database

Python scraper + SQLite database + Google Sheets sync + GitHub Actions annual refresh for publicly listed college baseball coach contact information.

## Scope

- NCAA Division 1
- NCAA Division 2
- NCAA Division 3
- NAIA
- NJCAA
- CCCAA
- NWAC
- Other two-year college baseball programs

Contacts collected:

- Head Coaches
- Baseball-specific Assistant Coaches
- Recruiting Coordinators

Only public information from official school athletics websites should be collected.

## Google Sheet

Target sheet name: `College Baseball Coach Recruiting Database`

Current spreadsheet ID:

```text
1rXNHyhF2iiczLDfQWH0OinSfVXCKl8-2Z2B6RHeUixg
```

## Setup Steps

### 1. Create Google Cloud credentials

Google's Sheets API requires a Google Cloud project and enabled Google Sheets API. Google's Python quickstart lists Python, pip, a Google Cloud project, and a Google account as prerequisites.

For this project, use a **service account** rather than OAuth desktop auth because GitHub Actions needs non-interactive access.

Steps:

1. Go to Google Cloud Console.
2. Create a project, for example: `College Baseball Coach Database`.
3. Enable the Google Sheets API.
4. Create a service account.
5. Create a JSON key for that service account.
6. Copy the service account email address.
7. Share your Google Sheet with the service account email as **Editor**.

### 2. Add GitHub repository secrets

In GitHub:

`Repository > Settings > Secrets and variables > Actions > New repository secret`

Add:

```text
SPREADSHEET_ID=1rXNHyhF2iiczLDfQWH0OinSfVXCKl8-2Z2B6RHeUixg
GOOGLE_SERVICE_ACCOUNT_JSON=<full contents of the downloaded service account JSON file>
```

### 3. Upload this project to GitHub

Commit all files into your private GitHub repository.

### 4. Add the master school seed file

Create:

```text
data/seeds/schools_master.csv
```

Required columns:

```text
division,school,state,conference,athletics_website,baseball_page_url,staff_directory_url
```

A sample is included at:

```text
data/seeds/schools_sample.csv
```

### 5. Test locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m src.cbcoachdb.main run --seed data/seeds/schools_sample.csv --dry-run
```

### 6. Initialize Google Sheet tabs

After `service_account.json` is in the project root locally:

```bash
python -m src.cbcoachdb.main init-sheet
```

### 7. Run in GitHub Actions

Go to:

`Actions > Yearly College Baseball Coach Database Refresh > Run workflow`

The workflow also runs automatically every September 1.

## Important Notes

- Scraping logic must stay respectful of school websites.
- Do not scrape private, gated, or personal contact data.
- Some schools intentionally hide email addresses behind JavaScript or staff-directory widgets. Those schools will be placed in `Missing / Needs Manual Review`.
- The first full build requires a clean master school seed list. After that, annual refreshes become much easier.

## Next Development Steps

1. Build full `schools_master.csv` from NCAA, NAIA, NJCAA, CCCAA, NWAC, and other two-year program directories.
2. Expand parser adapters for common athletics website platforms, including Sidearm, PrestoSports, Stretch Internet, and school custom sites.
3. Add change detection comparing current scrape against prior database records.
4. Add email-format validation and broken-link checks.
5. Add manual override file for schools where staff pages are difficult to parse.
