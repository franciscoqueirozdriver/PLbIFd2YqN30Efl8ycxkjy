import os
import time
from typing import List, Dict, Optional, Any

import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError

from ._utils import iso_now

_CLIENT = None
_SPREADSHEET = None

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_client() -> gspread.Client:
    global _CLIENT
    if _CLIENT:
        return _CLIENT
    private_key = os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n")
    client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
    creds = Credentials.from_service_account_info(
        {
            "type": "service_account",
            "private_key": private_key,
            "client_email": client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=SCOPES,
    )
    _CLIENT = gspread.authorize(creds)
    return _CLIENT


def _get_sheet(tab: str) -> gspread.Worksheet:
    global _SPREADSHEET
    client = _get_client()
    if _SPREADSHEET is None:
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        _SPREADSHEET = client.open_by_key(spreadsheet_id)
    return _SPREADSHEET.worksheet(tab)


_BACKOFF_BASE = 1
_BACKOFF_MAX = 32


def _with_backoff(func, *args, **kwargs):
    delay = _BACKOFF_BASE
    while True:
        try:
            return func(*args, **kwargs)
        except APIError as e:  # type: ignore[no-redef]
            status = getattr(e.response, "status_code", None)
            if status and (status == 429 or 500 <= status < 600):
                time.sleep(delay)
                delay = min(delay * 2, _BACKOFF_MAX)
                continue
            raise


def get_rows(tab: str, *, filters: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None,
             limit: int = 50, cursor: Optional[int] = None) -> Dict[str, Any]:
    sheet = _get_sheet(tab)
    records = _with_backoff(sheet.get_all_records)
    if filters:
        def match(row):
            for k, v in filters.items():
                if str(row.get(k)) != str(v):
                    return False
            return True
        records = [r for r in records if match(r)]
    if order_by:
        records.sort(key=lambda r: r.get(order_by))
    start = cursor or 0
    end = start + limit
    page = records[start:end]
    next_cursor = end if end < len(records) else None
    return {"rows": page, "next_cursor": next_cursor, "total": len(records)}


def get_by_id(tab: str, id_col: str, id_val: str) -> Optional[Dict[str, Any]]:
    res = get_rows(tab, filters={id_col: id_val}, limit=1)
    rows = res.get("rows")
    return rows[0] if rows else None


def insert_rows(tab: str, list_of_dicts: List[Dict[str, Any]]) -> None:
    sheet = _get_sheet(tab)
    header = sheet.row_values(1)
    values = [[record.get(col, "") for col in header] for record in list_of_dicts]
    _with_backoff(sheet.append_rows, values)


def update_row(tab: str, id_col: str, id_val: str, patch_dict: Dict[str, Any]) -> bool:
    sheet = _get_sheet(tab)
    header = sheet.row_values(1)
    try:
        col = header.index(id_col) + 1
    except ValueError:
        return False
    column_values = sheet.col_values(col)
    try:
        row_index = column_values.index(id_val) + 1
    except ValueError:
        return False
    row_values = sheet.row_values(row_index)
    data = {h: row_values[i] if i < len(row_values) else "" for i, h in enumerate(header)}
    data.update(patch_dict)
    values = [[data.get(col, "") for col in header]]
    _with_backoff(sheet.update, f"A{row_index}:{gspread.utils.rowcol_to_a1(row_index, len(header))}", values)
    return True


def soft_delete(tab: str, id_col: str, id_val: str) -> bool:
    return update_row(tab, id_col, id_val, {"status": "archived", "updated_at": iso_now()})


def append_log(tab: str = "Logs", **fields: Any) -> None:
    try:
        insert_rows(tab, [fields])
    except Exception:
        pass
