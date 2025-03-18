from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
import pathlib

from datetime import datetime

from api.utils.elastic import ElasticsearchService
from app.managers.auth import oauth2_schema
from app.schemas.response.ffiles import SysFile
from app.managers.archive import ArchiveService
from fastapi import BackgroundTasks
from app.api.utils.do_file import syspath, check_name, write, get_mime, format_bytes_size, bucket_path, sanitize_path

from schemas.request.ffiles import FileResponseSchema

archive_service = ArchiveService()  # Configure with your base path
router = APIRouter(tags=["File"], prefix="/file")




@router.get("{url_path:path}", response_class=FileResponse, summary="download", dependencies=[Depends(oauth2_schema)])
async def download_file(path: pathlib.Path = Depends(syspath)):
    """download file"""
    if path.is_file():
        return FileResponse(path, filename=path.name)
    raise HTTPException(status_code=404)


@router.post("{url_path:path}", response_model=SysFile, summary="upload", dependencies=[Depends(oauth2_schema)])
async def upload_file(
        background_tasks: BackgroundTasks,
        path: pathlib.Path = Depends(syspath),
        file: UploadFile = File(...),
):
    """Upload file, trigger indexing in background"""

    if not path.is_dir():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}")

    if not file.filename:
        raise HTTPException(status_code=422, detail="Name cannot be empty")

    new_file = path / pathlib.Path(file.filename)

    if new_file.is_file():
        raise HTTPException(status_code=412, detail="File already exists")

    if not check_name(file.filename):
        raise HTTPException(status_code=422, detail=r"Name cannot contain \/:*?<>|")

    # Читаємо вміст файлу
    content = await file.read()
    await write(content, new_file)
    es = ElasticsearchService()
    # ✅ Додаємо задачу індексації у фон
    background_tasks.add_task(es.index_file, str(new_file))

    return SysFile(
        name=new_file.name,
        mime=get_mime(new_file),
        mtime=datetime.fromtimestamp(new_file.stat().st_mtime),
        ctime=datetime.fromtimestamp(new_file.stat().st_ctime),
        size=format_bytes_size(new_file),
    )

@router.put("{url_path:path}", summary="mv", dependencies=[Depends(oauth2_schema)])
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


@router.delete("{url_path:path}", summary="rm -f", dependencies=[Depends(oauth2_schema)])
def remove_file(background_tasks: BackgroundTasks, path: pathlib.Path = Depends(syspath)):
    """remove file"""
    if not path.is_file():
        raise HTTPException(status_code=404)
    try:
        es = ElasticsearchService()
        pathlib.Path.unlink(path)
        background_tasks.add_task(es.delete_file_index, str(path))
    except FileNotFoundError:
        raise HTTPException(status_code=404)
    except OSError as e:
        raise HTTPException(status_code=412, detail=f"{e}")



