import os
import sys
from collections import Counter

from langchain.tools import tool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from services.drive_client import get_drive_service


@tool("list_drive_summary")
def list_drive_summary() -> str:
    """
    Returns a summary of all files in the Google Drive folder grouped by type.
    Use this when the user asks 'what files do you have?', 'what is in the drive?',
    'show me everything', or any general overview request.
    """
    try:
        service = get_drive_service()
        results = service.files().list(
            q=f"'{settings.drive_folder_id}' in ancestors and trashed = false",
            fields="files(name, mimeType)",
            pageSize=100,
        ).execute()

        files = results.get("files", [])
        if not files:
            return "The Drive folder appears to be empty or the agent cannot access it."

        type_counter = Counter()
        for f in files:
            mime = f.get("mimeType", "unknown")
            if "pdf" in mime:
                type_counter["📕 PDFs"] += 1
            elif "spreadsheet" in mime or "excel" in mime or "csv" in mime:
                type_counter["📊 Spreadsheets"] += 1
            elif "document" in mime or "word" in mime:
                type_counter["📝 Documents"] += 1
            elif "presentation" in mime or "powerpoint" in mime:
                type_counter["🎞️ Presentations"] += 1
            elif "image" in mime:
                type_counter["🖼️ Images"] += 1
            elif "folder" in mime:
                type_counter["📁 Folders"] += 1
            elif "video" in mime:
                type_counter["🎬 Videos"] += 1
            else:
                type_counter["📄 Other"] += 1

        lines = [f"**Drive contains {len(files)} total files:**\n"]
        for ftype, count in type_counter.most_common():
            lines.append(f"- {ftype}: **{count}**")
        lines.append("\nAsk me to search for any of these — I can filter by name, content, or date!")
        return "\n".join(lines)

    except Exception as e:
        return f"Error listing Drive contents: {str(e)}"