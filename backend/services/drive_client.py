import json
from functools import lru_cache

from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import settings


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


@lru_cache(maxsize=1)
def get_drive_service():
    """
    Returns a cached Google Drive API service client.
    In production, reads credentials from the GOOGLE_SERVICE_ACCOUNT_JSON env var.
    Locally, falls back to a service_account.json file in the project root.
    """
    sa_json = settings.google_service_account_json
    if sa_json:
        info = json.loads(sa_json)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = service_account.Credentials.from_service_account_file(
            "service_account.json", scopes=SCOPES
        )
    return build("drive", "v3", credentials=creds)