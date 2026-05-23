"""Disabled-by-default Google Drive upload placeholder.

Required future configuration should live in environment variables or
Streamlit secrets, never in source code:

- GOOGLE_DRIVE_FOLDER_ID: target shared Drive folder ID
- GOOGLE_SERVICE_ACCOUNT_JSON: service account JSON contents, or
- GOOGLE_APPLICATION_CREDENTIALS: path to a service account JSON file

The current app does not upload files unless real Google Drive API integration
is added. This avoids pretending that protected survey files were synced.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def drive_upload_configured() -> bool:
    """Return whether the minimum future Drive settings appear to be present."""
    folder_id = _get_config_value("GOOGLE_DRIVE_FOLDER_ID")
    credentials = _get_config_value("GOOGLE_SERVICE_ACCOUNT_JSON") or _get_config_value(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    return bool(folder_id and credentials)


def upload_files_to_drive(
    file_paths: Iterable[str | Path],
    folder_id: str | None = None,
) -> dict[str, object]:
    """Placeholder for future Drive upload integration.

    This function is intentionally safe: it returns a status message and never
    claims success. Add Google Drive API client code here after credentials,
    folder ownership, and access controls are finalized.
    """
    configured_folder = folder_id or _get_config_value("GOOGLE_DRIVE_FOLDER_ID")
    credentials = _get_config_value("GOOGLE_SERVICE_ACCOUNT_JSON") or _get_config_value(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    existing_files = [str(Path(path)) for path in file_paths if Path(path).exists()]

    if not configured_folder or not credentials:
        return {
            "enabled": False,
            "uploaded": [],
            "files_found": existing_files,
            "message": (
                "Google Drive upload is disabled because Drive folder ID and "
                "service account credentials are not configured."
            ),
        }

    return {
        "enabled": False,
        "uploaded": [],
        "files_found": existing_files,
        "message": (
            "Google Drive credentials were detected, but upload code is not "
            "implemented yet. No files were uploaded."
        ),
    }


def _get_config_value(name: str) -> str | None:
    env_value = os.getenv(name)
    if env_value:
        return env_value

    try:
        import streamlit as st

        value = st.secrets.get(name)
        return str(value) if value else None
    except Exception:
        return None
