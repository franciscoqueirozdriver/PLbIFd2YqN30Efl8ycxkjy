import os
from typing import List, Dict, Any

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

_spreadsheet = None


def _get_spreadsheet():
    private_key = os.getenv("GOOGLE_PRIVATE_KEY")
    client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    if not private_key or not client_email or not spreadsheet_id:
        raise RuntimeError("Missing Google Sheets credentials")

    private_key = private_key.replace("\\n", "\n")
    creds_info = {
        "type": "service_account",
        "private_key": private_key,
        "client_email": client_email,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
    client = gspread.authorize(credentials)
    return client.open_by_key(spreadsheet_id)


def _worksheet(name: str):
    global _spreadsheet
    if _spreadsheet is None:
        _spreadsheet = _get_spreadsheet()
    return _spreadsheet.worksheet(name)


def insert_rows(sheet_name: str, rows: List[Dict[str, Any]]):
    ws = _worksheet(sheet_name)
    if not rows:
        return
    values = [list(r.values()) for r in rows]
    ws.append_rows(values, value_input_option="USER_ENTERED")


def clear_and_insert(sheet_name: str, rows: List[Dict[str, Any]]):
    ws = _worksheet(sheet_name)
    ws.clear()
    if not rows:
        return
    header = list(rows[0].keys())
    ws.append_row(header)
    values = [list(r.values()) for r in rows]
    if values:
        ws.append_rows(values, value_input_option="USER_ENTERED")


def append_row(sheet_name: str, row: Dict[str, Any]):
    ws = _worksheet(sheet_name)
    ws.append_row(list(row.values()), value_input_option="USER_ENTERED")


def get_rows(sheet_name: str):
    ws = _worksheet(sheet_name)
    return ws.get_all_records()
