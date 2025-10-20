from fastapi import APIRouter, Depends, HTTPException, status, Query
from pathlib import Path
import os
from ..api.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/files", tags=["files"])

# Security: Define allowed directories
ALLOWED_BASE_PATHS = [
    os.path.expanduser("~"),  # User home directory
    "/tmp",  # Temporary files
]

# Maximum file size to read (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

def is_safe_path(file_path: str) -> bool:
    """Validate that the file path is within allowed directories"""
    try:
        abs_path = Path(file_path).resolve()

        # Check if path is within any allowed base path
        for base_path in ALLOWED_BASE_PATHS:
            base = Path(base_path).resolve()
            try:
                abs_path.relative_to(base)
                return True
            except ValueError:
                continue

        return False
    except Exception:
        return False

@router.get("")
async def get_file_content(
    path: str = Query(..., description="Absolute path to the file"),
    current_user: User = Depends(get_current_user)
):
    """Get file content with path validation

    Security measures:
    - Path traversal prevention
    - Directory whitelist
    - File size limits
    - User authentication required
    """

    # Validate path safety
    if not is_safe_path(path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this file path is not allowed"
        )

    file_path = Path(path)

    # Check file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Check it's a file, not a directory
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path is not a file"
        )

    # Check file size
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (max {MAX_FILE_SIZE / 1024 / 1024}MB)"
        )

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        return {
            "path": str(file_path),
            "size": file_size,
            "content": content,
            "encoding": "utf-8"
        }
    except UnicodeDecodeError:
        # Try binary mode for non-text files
        with open(file_path, 'rb') as f:
            content = f.read()
        return {
            "path": str(file_path),
            "size": file_size,
            "content": content.hex(),
            "encoding": "hex"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}"
        )
