"""
Translates structured search parameters into a valid Google Drive API q string.
The LangGraph agent calls build_query() via tool arguments — never constructs
raw query strings itself.
"""

from datetime import datetime, timedelta
from typing import Optional


MIME_TYPE_MAP = {
    "pdf": "application/pdf",
    "doc": "application/vnd.google-apps.document",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "google doc": "application/vnd.google-apps.document",
    "sheet": "application/vnd.google-apps.spreadsheet",
    "sheets": "application/vnd.google-apps.spreadsheet",
    "spreadsheet": "application/vnd.google-apps.spreadsheet",
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "csv": "text/csv",
    "slides": "application/vnd.google-apps.presentation",
    "presentation": "application/vnd.google-apps.presentation",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image": "image/",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "folder": "application/vnd.google-apps.folder",
    "form": "application/vnd.google-apps.form",
    "video": "video/",
    "txt": "text/plain",
    "text": "text/plain",
}

RELATIVE_DATE_MAP = {
    "today": 0,
    "yesterday": 1,
    "this week": 7,
    "last week": 14,
    "this month": 30,
    "last month": 60,
    "this year": 365,
}


def build_query(
    name_contains: Optional[str] = None,
    name_exact: Optional[str] = None,
    file_type: Optional[str] = None,
    full_text: Optional[str] = None,
    modified_after: Optional[str] = None,
    modified_before: Optional[str] = None,
    folder_id: Optional[str] = None,
) -> str:
    """
    Build a Google Drive API q parameter string from structured inputs.
    All parameters are optional and combined with AND logic.
    """
    clauses = []

    if name_exact:
        safe = name_exact.replace("'", "\\'")
        clauses.append(f"name = '{safe}'")

    if name_contains:
        safe = name_contains.replace("'", "\\'")
        clauses.append(f"name contains '{safe}'")

    if full_text:
        safe = full_text.replace("'", "\\'")
        clauses.append(f"fullText contains '{safe}'")

    if file_type:
        ft = file_type.lower().strip()
        mime = MIME_TYPE_MAP.get(ft)
        if mime:
            if mime.endswith("/"):
                clauses.append(f"mimeType contains '{mime}'")
            else:
                clauses.append(f"mimeType = '{mime}'")

    if modified_after:
        dt = _resolve_date(modified_after)
        if dt:
            clauses.append(f"modifiedTime > '{dt}'")

    if modified_before:
        dt = _resolve_date(modified_before)
        if dt:
            clauses.append(f"modifiedTime < '{dt}'")

    if folder_id:
        clauses.append(f"'{folder_id}' in ancestors")

    clauses.append("trashed = false")
    return " and ".join(clauses)


def _resolve_date(date_str: str) -> Optional[str]:
    """Convert relative date strings or ISO YYYY-MM-DD to Drive API format."""
    s = date_str.lower().strip()
    for key, days_ago in RELATIVE_DATE_MAP.items():
        if key in s:
            dt = datetime.utcnow() - timedelta(days=days_ago)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None