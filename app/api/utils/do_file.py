import pathlib
from pathlib import Path
import fastapi
import aiofiles
import re
import filetype
import mimetypes
from typing import Optional, Union
from functools import singledispatch

import psutil
from fastapi import HTTPException

from app.config.helpers import get_project_root

bucket_path = get_project_root() / "app" / "uploaded_files"


def syspath(url_path: str = fastapi.Path(...)) -> Path:
    return bucket_path / Path('.' + url_path)


def format_bytes_size(file: Path) -> str:
    bytes_size = Path.stat(file).st_size
    series = ['B', 'KB', 'MB', 'GB', 'TB']
    for _ in series:
        if bytes_size < 1024:
            return f"{bytes_size:.4g}{_}"  # reserve 4 significant digits
        bytes_size /= 1024
    return f'{bytes_size:.4g}PB'


def check_name(name: str) -> bool:
    return not re.search(r'[\\\/\:\*\?\"\<\>\|]', name)


def get_mime(file: Path) -> Optional[str]:
    if (type := filetype.guess(file)) is None:
        return mimetypes.guess_type(file.name)[0]
    return type.mime


def get_system_stats():
    # Перевірка, чи існує директорія
    directory = Path(bucket_path)
    print(directory)
    if not directory.exists() or not directory.is_dir():
        return None

    # Підрахуємо кількість файлів і папок у конкретній директорії
    total_files = 0
    total_folders = 0
    total_size = 0  # у байтах

    # Використовуємо pathlib для обходу директорії
    for file in directory.rglob('*'):
        if file.is_file():
            total_files += 1
            total_size += file.stat().st_size
        elif file.is_dir():
            total_folders += 1

    # Отримуємо статистику про використання системних ресурсів
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    used_memory = memory_info.used / (1024 * 1024 * 1024)  # в МБ
    total_memory = memory_info.total / (1024 * 1024 * 1024)  # в МБ

    return {
        "cpu_usage": cpu_usage,
        "total_files": total_files,
        "total_folders": total_folders,
        "total_size": round(total_size / (1024 * 1024), 3),  # Розмір у МБ з 3 цифрами після коми
        "used_memory": round(used_memory, 3),
        "total_memory": round(total_memory, 3)
    }


def sanitize_path(path: pathlib.Path) -> pathlib.Path:
    """Ensure the path is safe and within the allowed directory."""
    try:
        resolved_path = path.resolve(strict=False)

        def syspath(url_path: str = fastapi.Path(...)) -> Path:
            return bucket_path / Path('.' + url_path)

        if not resolved_path.is_relative_to(bucket_path):
            raise ValueError("Path traversal detected")
        return resolved_path
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {e}")


async def read(file: Path) -> bytes:
    async with aiofiles.open(file, 'rb') as f:
        return await f.read()


@singledispatch
async def write(data: Union[str, bytes], file: Path):
    pass


@write.register(bytes)
async def _(data: bytes, file: Path):
    async with aiofiles.open(file, "wb+") as f:
        await f.write(data)


@write.register(str)
async def _(data: str, file: Path):
    async with aiofiles.open(file, "w+", encoding='utf-8') as f:
        await f.write(data)
