import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException

from api.utils.do_file import sanitize_path, bucket_path, syspath
from schemas.request.ffiles import ArchiveRequest
from schemas.response.ffiles import ArchiveResponse


class ArchiveService:
    """Service class for handling archive operations"""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def create_archive(self, request: ArchiveRequest) -> ArchiveResponse:
        """
        Create a zip archive from the specified directory

        Args:
            request: ArchiveRequest model containing archive parameters

        Returns:
            ArchiveResponse with archive details

        Raises:
            HTTPException: If directory not found or archive creation fails
        """
        directory_path = syspath('/')
        archive_path = directory_path / request.archive_name

        try:
            file_count = 0

            # Виключаємо архів з процесу додавання
            if archive_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail="Archive file already exists in the directory."
                )

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                # Проходимо по всіх файлах і підкаталогах
                for file_path in directory_path.rglob('*'):
                    if file_path.is_file():
                        # Виключаємо сам архів із додавання
                        if file_path == archive_path:
                            continue

                        relative_path = file_path.relative_to(directory_path)
                        archive.write(file_path, arcname=str(relative_path))
                        file_count += 1

            return ArchiveResponse(
                archive_url=f"/downloads/{request.archive_name}",
                message="Archive created successfully",
                created_at=datetime.now(),
                file_count=file_count
            )

        except Exception as e:
            # Логування помилки (можна використовувати logger, якщо він є)
            # logger.error(f"Error creating archive: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating archive: {str(e)}"
            )
