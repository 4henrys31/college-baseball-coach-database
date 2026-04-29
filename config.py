import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    spreadsheet_id: str = os.getenv('SPREADSHEET_ID', '1rXNHyhF2iiczLDfQWH0OinSfVXCKl8-2Z2B6RHeUixg')
    google_service_account_file: str = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')
    database_path: str = os.getenv('DATABASE_PATH', 'college_baseball_coaches.sqlite')
    user_agent: str = os.getenv('USER_AGENT', 'CollegeBaseballCoachDatabaseBot/1.0 contact: 4henrys31@gmail.com')

settings = Settings()
