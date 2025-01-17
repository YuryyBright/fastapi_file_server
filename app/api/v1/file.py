from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
import pathlib

from datetime import datetime
from app.managers.auth import oauth2_schema
from app.schemas.response.ffiles import SysFile
from managers.archive import ArchiveService

from ..utils.do_file import syspath, check_name, write, get_mime, format_bytes_size, bucket_path, sanitize_path

archive_service = ArchiveService(pathlib.Path("bucket"))  # Configure with your base path
router = APIRouter(tags=["File"], prefix="/file")




@router.get("{url_path:path}", response_class=FileResponse, summary="download")
async def download_file(path: pathlib.Path = Depends(syspath)):
    """download file"""
    if path.is_file():
        return FileResponse(path, filename=path.name)
    raise HTTPException(status_code=404)


@router.post("{url_path:path}", response_model=SysFile, summary="upload")
async def upload_file(path: pathlib.Path = Depends(syspath), file: UploadFile = File(...)):
    """upload file to specified folder"""
    if not path.is_dir():
        raise HTTPException(status_code=404)
    if not file.filename:
        raise HTTPException(status_code=422, detail="Name cannot be empty")
    new_file = path / pathlib.Path(file.filename)
    if new_file.is_file():
        raise HTTPException(status_code=412, detail="File already exists")
    if not check_name(file.filename):
        raise HTTPException(status_code=422, detail=r"Name cannot contain \/:*?<>|")
    content = await file.read()
    await write(content, new_file)
    return SysFile(
        name=new_file.name,
        mime=get_mime(new_file),
        mtime=datetime.fromtimestamp(
            pathlib.Path.stat(new_file).st_mtime),
        ctime=datetime.fromtimestamp(
            pathlib.Path.stat(new_file).st_ctime),
        size=format_bytes_size(new_file)
    )


@router.put("{url_path:path}", summary="mv")
def move_file(path: pathlib.Path = Depends(syspath), new_path: str = Form(...)):
    """set new path(new name)"""
    if not path.is_file():
        raise HTTPException(status_code=404)
    try:
        path.rename(bucket_path / pathlib.Path("." + new_path))
    except FileExistsError:
        raise HTTPException(status_code=412, detail="Name already exists")
    except OSError as e:
        raise HTTPException(status_code=412, detail=f"{e}")


@router.delete("{url_path:path}", summary="rm -f")
def remove_file(path: pathlib.Path = Depends(syspath)):
    """remove file"""
    if not path.is_file():
        raise HTTPException(status_code=404)
    try:
        pathlib.Path.unlink(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404)
    except OSError as e:
        raise HTTPException(status_code=412, detail=f"{e}")



