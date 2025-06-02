"""Routes for User listing and control."""

from collections.abc import Sequence
from typing import Annotated, Optional, Union

from fastapi import APIRouter, Depends, Request, status, Response, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.utils.elastic import ElasticsearchService
from app.api.v1.file import archive_service
from app.database.db import get_database
from app.managers.auth import can_edit_user, is_admin, oauth2_schema
from app.managers.user import UserManager
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.request.user import UserChangePasswordRequest, UserEditRequest
from app.schemas.response.user import MyUserResponse, UserResponse
from app.managers.archive import ArchiveService
from app.schemas.request.ffiles import ArchiveRequest, FileResponseSchema
from app.schemas.response.ffiles import ErrorResponse, ArchiveResponse

router = APIRouter(tags=["Users"], prefix="/users")


# @router.get(
#     "/",
#     dependencies=[Depends(oauth2_schema), Depends(is_admin)],
#     response_model=Union[UserResponse, list[UserResponse]],
# )
# async def get_users(
#     db: Annotated[AsyncSession, Depends(get_database)],
#     user_id: Optional[int] = None,
# ) -> Union[Sequence[User], User]:
#     """Get all users or a specific user by their ID.
#
#     user_id is optional, and if omitted then all Users are returned.
#
#     This route is only allowed for Admins.
#     """
#     if user_id:
#         return await UserManager.get_user_by_id(user_id, db)
#     return await UserManager.get_all_users(db)


@router.get(
    "/all_users",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    response_model=Union[UserResponse, list[UserResponse]],
)
async def get_users(
    db: Annotated[AsyncSession, Depends(get_database)],
    user_id: Optional[int] = None,
) -> Union[Sequence[User], User]:
    """Get all users or a specific user by their ID.

    user_id is optional, and if omitted then all Users are returned.

    This route is only allowed for Admins.
    """
    if user_id:
        return await UserManager.get_user_by_id(user_id, db)
    return await UserManager.get_all_users(db)

@router.get(
    "/me",
    dependencies=[Depends(oauth2_schema)],
    response_model=MyUserResponse,
    name="get_my_user_data",
)
async def get_my_user(
    request: Request, db: Annotated[AsyncSession, Depends(get_database)]
) -> User:
    """Get the current user's data only."""
    my_user: int = request.state.user.id
    return await UserManager.get_user_by_id(my_user, db)


@router.post(
    "/{user_id}/make-admin",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def make_admin(
    user_id: int, db: Annotated[AsyncSession, Depends(get_database)]
) -> None:
    """Make the User with this ID an Admin."""
    await UserManager.change_role(RoleType.admin, user_id, db)


@router.post(
    "/{user_id}/password",
    dependencies=[Depends(oauth2_schema), Depends(can_edit_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    user_id: int,
    user_data: UserChangePasswordRequest,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Change the password for the specified user.

    Can only be done by an Admin, or the specific user that matches the user_id.
    """
    await UserManager.change_password(user_id, user_data, db)


@router.post(
    "/{user_id}/ban",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def ban_user(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Ban the specific user Id.

    Admins only. The Admin cannot ban their own ID!
    """
    await UserManager.set_ban_status(user_id, True, request.state.user.id, db)


@router.post(
    "/{user_id}/unban",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unban_user(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Ban the specific user Id.

    Admins only.
    """
    await UserManager.set_ban_status(user_id, False, request.state.user.id, db)


@router.put(
    "/{user_id}",
    dependencies=[Depends(oauth2_schema), Depends(can_edit_user)],
    status_code=status.HTTP_200_OK,
    response_model=MyUserResponse,
)
async def edit_user(
    user_id: int,
    user_data: UserEditRequest,
    db: Annotated[AsyncSession, Depends(get_database)],
) -> Union[User, None]:
    """Update the specified User's data.

    Available for the specific requesting User, or an Admin.
    """
    await UserManager.update_user(user_id, user_data, db)
    return await db.get(User, user_id)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int, db: Annotated[AsyncSession, Depends(get_database)]
) -> None:
    """Delete the specified User by user_id.

    Admin only.
    """
    await UserManager.delete_user(user_id, db)


@router.post(
    "/archive",
    response_model=ArchiveResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Create and download ZIP archive",
    description="Create a ZIP archive containing all files from the specified directory"
)
async def create_archive(
        request: ArchiveRequest,
        service: ArchiveService = Depends(lambda: archive_service)
):
    """
    Create a ZIP archive endpoint

    Args:
        request: Archive creation parameters
        service: Archive service instance

    Returns:
        ArchiveResponse with download URL and metadata
    """

    return service.create_archive(request)


@router.get(
    "/get_unindexed_files",
    dependencies=[Depends(oauth2_schema)],
    response_model=FileResponseSchema,
    summary="Get lis fo unindexed files",)
async def get_unindexed_files() -> FileResponseSchema:
    """Retrun lis fo unindexed files"""
    try:
        es_service = ElasticsearchService()
        unindexed_files = await es_service.get_unindexed_files()
        return FileResponseSchema(unindexed_files=unindexed_files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання даних: {str(e)}")


@router.get(
    "/index_all_unindexed_files",
    dependencies=[Depends(oauth2_schema)],
    response_model=FileResponseSchema,
    summary="Index all unindexed files in the background"
)
async def index_all_unindexed_files(background_tasks: BackgroundTasks) -> FileResponseSchema:
    """Запускає індексацію всіх непроіндексованих файлів у фоновому режимі."""
    try:
        es_service = ElasticsearchService()
        # Запускаємо індексацію файлів у фоновому режимі
        background_tasks.add_task(es_service.index_all_unindexed_files)
        # Отримуємо список непроіндексованих файлів
        es_service = ElasticsearchService()
        unindexed_files = await es_service.get_unindexed_files()
        return FileResponseSchema(unindexed_files=unindexed_files)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання даних: {str(e)}")
# @router.post("/unarchive", summary="Import from Archive", dependencies=[Depends(oauth2_schema)])
# def import_from_archive(archive: UploadFile = File(...), extract_to: str = Form("")):
#     """Extract files from an uploaded archive."""
#     extract_path = sanitize_path(bucket_path / extract_to)
#
#     if not extract_path.is_dir():
#         try:
#             extract_path.mkdir(parents=True, exist_ok=True)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to create directory: {e}")
#
#     try:
#         with zipfile.ZipFile(archive.file, 'r') as zip_ref:
#             zip_ref.extractall(extract_path)
#     except zipfile.BadZipFile:
#         raise HTTPException(status_code=422, detail="Invalid archive format")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error extracting archive: {e}")
#
#     return {"message": "Archive extracted successfully", "path": str(extract_path)}