import os
import time
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetSchemaError(Exception):
    ...


def _client():
    key = os.environ["GOOGLE_PRIVATE_KEY"]
    key = key.strip().strip('"').strip("'").replace("\\n", "\n")
    email = os.environ["GOOGLE_CLIENT_EMAIL"]
    creds = Credentials.from_service_account_info({
        "type": "service_account",
        "client_email": email,
        "private_key": key,
        "token_uri": "https://oauth2.googleapis.com/token"
    }, scopes=SCOPES)
    return gspread.authorize(creds)


def ws(tab: str):
    sid = os.environ["SPREADSHEET_ID"]
    return _client().open_by_key(sid).worksheet(tab)


def ensure_headers(tab: str, expected: list[str]):
    w = ws(tab)
    got = w.row_values(1)
    missing = [h for h in expected if h not in got]
    if missing or got[: len(expected)] != expected:
        raise SheetSchemaError(
            f"Aba '{tab}' inválida. Faltando: {missing}. Atuais: {got}. Esperado: {expected}")
    return w, got


def append_rows(tab: str, dicts: list[dict], expected_headers: list[str]):
    w, _ = ensure_headers(tab, expected_headers)
    rows = [[("" if d.get(h) is None else d.get(h)) for h in expected_headers] for d in dicts]
    delay = 0.5
    for _ in range(5):
        try:
            w.append_rows(rows, value_input_option="RAW")
            return
        except gspread.exceptions.APIError as e:  # noqa: BLE001
            code = getattr(getattr(e, "response", None), "status_code", 0)
            if code in (429, 500, 503):
                time.sleep(delay)
                delay *= 2
                continue
            raise
