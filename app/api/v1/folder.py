from fastapi import APIRouter, Depends, Form, HTTPException
import shutil


import pathlib
from datetime import datetime
from typing import Union, List

from app.api.utils.do_file import syspath, get_mime, format_bytes_size, check_name, bucket_path
from app.schemas.response.ffiles import SysFile, SysFolder

folder = APIRouter(tags=["Folder"], prefix="/folder")

LS = List[Union[SysFile, SysFolder]]


@folder.get("{url_path:path}", response_model=LS, summary="ls")
def get_folder_dir(path: pathlib.Path = Depends(syspath)):
    """get all file_stat_info in specified folder"""
    if not path.is_dir():
        raise HTTPException(status_code=404)
    ls: LS = []
    for _ in path.iterdir():
        if _.is_dir():
            ls.append(SysFolder(
                name=_.name,
                mtime=datetime.fromtimestamp(pathlib.Path.stat(_).st_mtime),
                ctime=datetime.fromtimestamp(pathlib.Path.stat(_).st_ctime))
            )
        else:
            ls.append(SysFile(
                name=_.name,
                mime=get_mime(_),
                mtime=datetime.fromtimestamp(pathlib.Path.stat(_).st_mtime),
                ctime=datetime.fromtimestamp(pathlib.Path.stat(_).st_ctime),
                size=format_bytes_size(_))
            )
    return ls


@folder.post("{url_path:path}", response_model=SysFolder, summary="mkdir")
def create_folder(path: pathlib.Path = Depends(syspath), dirname: str = Form(...)):
    """create a folder in specified folder"""
    if not path.is_dir():
        raise HTTPException(status_code=404)
    dirname = dirname.strip()
    if not dirname:
        raise HTTPException(status_code=422, detail="Name cannot be a blank string")
    if not check_name(dirname):
        raise HTTPException(status_code=422, detail=r"Name cannot contain \/:*?<>|")
    try:
        new_dir = path / pathlib.Path(dirname)
        new_dir.mkdir(parents=False, exist_ok=False)
        return SysFolder(
            name=dirname,
            mtime=datetime.fromtimestamp(pathlib.Path.stat(new_dir).st_mtime),
            ctime=datetime.fromtimestamp(pathlib.Path.stat(new_dir).st_ctime))
    except FileNotFoundError:
        raise HTTPException(status_code=404)
    except FileExistsError:
        raise HTTPException(status_code=412, detail="Name already exists")
    except OSError as e:
        raise HTTPException(status_code=412, detail=f"{e}")


@folder.put("{url_path:path}", summary="mv")
def move_folder(path: pathlib.Path = Depends(syspath), new_path: str = Form(...)):
    """set new path(new name)"""
    if not path.is_dir():
        raise HTTPException(status_code=404)
    try:
        path.rename(bucket_path / pathlib.Path("." + new_path))
    except FileExistsError:
        raise HTTPException(status_code=412, detail="Name already exists")
    except OSError as e:
        raise HTTPException(status_code=412, detail=f"{e}")


@folder.delete("{url_path:path}", summary="rm -rf")
def remove_folder(path: pathlib.Path = Depends(syspath)):
    """remove empty folder and non-empty folder"""
    if path == bucket_path:
        raise HTTPException(status_code=422, detail="Cannot remove root folder")
    """
    try:
        pathlib.Path.rmdir(path) # rm -f
    except FileNotFoundError:
        raise HTTPException(status_code=404)
    except OSError:
        raise HTTPException(status_code=412, detail="The folder is not empty")
    """
    try:
        shutil.rmtree(path)  # rm -rf
    except FileNotFoundError:
        raise HTTPException(status_code=404)
    except OSError as e:
        raise HTTPException(status_code=412, detail=f"{e}")