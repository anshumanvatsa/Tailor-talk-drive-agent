import os
import sys
from typing import Optional

from langchain.tools import tool
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from services.drive_client import get_drive_service
from services.query_builder import build_query


class DriveSearchInput(BaseModel):
    name_contains: Optional[str] = Field(None, description="Partial filename keyword to search for, e.g. 'invoice'")
    name_exact: Optional[str] = Field(None, description="Exact complete filename to match")
    file_type: Optional[str] = Field(None, description="File type keyword: pdf, sheet, doc, image, slides, excel, csv, txt, folder")
    full_text: Optional[str] = Field(None, description="Keyword to search within file contents")
    modified_after: Optional[str] = Field(None, description="Find files modified after this date. Use ISO date YYYY-MM-DD or relative terms like 'last week', 'this month', 'yesterday'")
    modified_before: Optional[str] = Field(None, description="Find files modified before this date. Use ISO date YYYY-MM-DD or relative terms")


@tool("search_drive_files", args_schema=DriveSearchInput)
def search_drive_files(
    name_contains: Optional[str] = None,
    name_exact: Optional[str] = None,
    file_type: Optional[str] = None,
    full_text: Optional[str] = None,
    modified_after: Optional[str] = None,
    modified_before: Optional[str] = None,
) -> str:
    """
    Search for files in the Google Drive folder. Use this tool whenever the user wants to
    find, locate, filter, or discover files. Combine parameters for precise results.
    Always use this tool for file searches — never guess file names.
    """
    try:
        q = build_query(
            name_contains=name_contains,
            name_exact=name_exact,
            file_type=file_type,
            full_text=full_text,
            modified_after=modified_after,
            modified_before=modified_before,
            folder_id=settings.drive_folder_id,
        )

        service = get_drive_service()
        results = service.files().list(
            q=q,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink, webContentLink)",
            pageSize=15,
            orderBy="modifiedTime desc",
        ).execute()

        files = results.get("files", [])
        if not files:
            return (
                f"No files found matching your query.\n"
                f"Drive query used: `{q}`\n"
                f"Try broader search terms or a different file type."
            )

        lines = [f"**Found {len(files)} file(s):**\n"]
        for f in files:
            emoji = _mime_to_emoji(f.get("mimeType", ""))
            size = _format_size(f.get("size"))
            view_link = f.get("webViewLink", "")
            modified = f.get("modifiedTime", "")[:10]
            lines.append(
                f"{emoji} **[{f['name']}]({view_link})**\n"
                f"&nbsp;&nbsp;&nbsp;📅 Modified: {modified} &nbsp;|&nbsp; 📦 Size: {size}\n"
            )
        return "\n".join(lines)

    except Exception as e:
        return f"Error searching Drive: {str(e)}"


def _mime_to_emoji(mime: str) -> str:
    if "pdf" in mime:
        return "📕"
    if "spreadsheet" in mime or "excel" in mime or "csv" in mime:
        return "📊"
    if "document" in mime or "word" in mime:
        return "📝"
    if "presentation" in mime or "powerpoint" in mime:
        return "🎞️"
    if "image" in mime:
        return "🖼️"
    if "video" in mime:
        return "🎬"
    if "folder" in mime:
        return "📁"
    if "text" in mime:
        return "📃"
    return "📄"


def _format_size(size_str) -> str:
    if not size_str:
        return "N/A"
    try:
        size = int(size_str)
        if size < 1024:
            return f"{size} B"
        if size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        return f"{size / 1024 ** 2:.1f} MB"
    except (ValueError, TypeError):
        return "N/A"