import os
import sys

from langchain.tools import tool
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.drive_client import get_drive_service


class DriveMetadataInput(BaseModel):
    file_id: str = Field(..., description="The Google Drive file ID to get details for")


@tool("get_file_details", args_schema=DriveMetadataInput)
def get_file_details(file_id: str) -> str:
    """
    Get detailed metadata about a specific file using its Google Drive file ID.
    Use this when the user wants to know more about a specific file shown in search results.
    """
    try:
        service = get_drive_service()
        f = service.files().get(
            fileId=file_id,
            fields="id,name,mimeType,size,createdTime,modifiedTime,description,webViewLink,webContentLink,owners,lastModifyingUser",
        ).execute()

        owner = f.get("owners", [{}])[0].get("displayName", "Unknown")
        last_editor = f.get("lastModifyingUser", {}).get("displayName", "Unknown")
        description = f.get("description") or "No description"
        size = _format_size(f.get("size"))
        view_link = f.get("webViewLink", "N/A")
        download_link = f.get("webContentLink", "N/A")

        return (
            f"**{f['name']}**\n\n"
            f"- 📅 Created: {f.get('createdTime', '?')[:10]}\n"
            f"- ✏️ Last modified: {f.get('modifiedTime', '?')[:10]}\n"
            f"- 👤 Owner: {owner}\n"
            f"- 🖊️ Last edited by: {last_editor}\n"
            f"- 📦 Size: {size}\n"
            f"- 📋 Description: {description}\n"
            f"- 🔗 [Open in Drive]({view_link})\n"
            f"- ⬇️ [Download]({download_link})\n"
        )
    except Exception as e:
        return f"Error fetching file details: {str(e)}"


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