from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
import pathlib
import shutil
import zipfile
from typing import List
from datetime import datetime
from app.managers.auth import oauth2_schema
from app.schemas.response.ffiles import SysFile
from ..utils.do_file import syspath, check_name, write, get_mime, format_bytes_size, bucket_path

file_router = APIRouter(tags=["File"], prefix="/file")


def sanitize_path(path: pathlib.Path) -> pathlib.Path:
    """Ensure the path is safe and within the allowed directory."""
    try:
        resolved_path = path.resolve(strict=False)
        if not resolved_path.is_relative_to(bucket_path):
            raise ValueError("Path traversal detected")
        return resolved_path
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {e}")


@file_router.get("{url_path:path}", response_class=FileResponse, summary="Download File", dependencies=[Depends(oauth2_schema)])
async def download_file(url_path: str):
    """Download a file by providing its relative path."""
    path = sanitize_path(bucket_path / url_path)
    if path.is_file():
        return FileResponse(path, filename=path.name)
    raise HTTPException(status_code=404, detail="File not found")


@file_router.post("{url_path:path}", response_model=SysFile, summary="Upload File", dependencies=[Depends(oauth2_schema)])
async def upload_file(url_path: str, file: UploadFile = File(...)):
    """Upload a file to the specified folder."""
    path = sanitize_path(bucket_path / url_path)
    if not path.is_dir():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create directory: {e}")

    if not file.filename:
        raise HTTPException(status_code=422, detail="Filename cannot be empty")

    if not check_name(file.filename):
        raise HTTPException(status_code=422, detail=r"Filename cannot contain \ / : * ? < > |")

    new_file = path / file.filename
    if new_file.exists():
        raise HTTPException(status_code=412, detail="File already exists")

    content = await file.read()
    await write(content, new_file)

    return SysFile(
        name=new_file.name,
        mime=get_mime(new_file),
        mtime=datetime.fromtimestamp(new_file.stat().st_mtime),
        ctime=datetime.fromtimestamp(new_file.stat().st_ctime),
        size=format_bytes_size(new_file.stat().st_size)
    )


@file_router.put("{url_path:path}", summary="Move File", dependencies=[Depends(oauth2_schema)])
def move_file(url_path: str, new_path: str = Form(...)):
    """Move or rename a file."""
    old_path = sanitize_path(bucket_path / url_path)
    new_path = sanitize_path(bucket_path / new_path)

    if not old_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        old_path.rename(new_path)
    except FileExistsError:
        raise HTTPException(status_code=412, detail="Destination file already exists")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error moving file: {e}")


@file_router.delete("{url_path:path}", summary="Delete File", dependencies=[Depends(oauth2_schema)])
def remove_file(url_path: str):
    """Delete a file."""
    path = sanitize_path(bucket_path / url_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        path.unlink()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")


@file_router.post("/archive", summary="Export to Archive", dependencies=[Depends(oauth2_schema)])
def export_to_archive(files: List[str] = Query(...), archive_name: str = Form("backup.zip")):
    """Create a zip archive containing specified files."""
    archive_path = sanitize_path(bucket_path / archive_name)

    try:
        with zipfile.ZipFile(archive_path, 'w') as archive:
            for file_name in files:
                file_path = sanitize_path(bucket_path / file_name)
                if not file_path.is_file():
                    raise HTTPException(status_code=404, detail=f"File not found: {file_name}")
                archive.write(file_path, arcname=file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating archive: {e}")

    return {"message": "Archive created successfully", "archive": str(archive_path)}


@file_router.post("/unarchive", summary="Import from Archive", dependencies=[Depends(oauth2_schema)])
def import_from_archive(archive: UploadFile = File(...), extract_to: str = Form("")):
    """Extract files from an uploaded archive."""
    extract_path = sanitize_path(bucket_path / extract_to)

    if not extract_path.is_dir():
        try:
            extract_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create directory: {e}")

    try:
        with zipfile.ZipFile(archive.file, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=422, detail="Invalid archive format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting archive: {e}")

    return {"message": "Archive extracted successfully", "path": str(extract_path)}
