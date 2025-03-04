import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "INSERT_YOUR_TOKEN_HERE")
    SPREADSHEET_ID = os.getenv(
        "SPREADSHEET_ID", "INSERT_YOUR_SPREADSHEET_ID_HERE"
    )
