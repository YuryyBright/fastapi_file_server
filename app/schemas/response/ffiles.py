from typing import Optional

from app.schemas.base import SysNode, SysNodeType


class SysFolder(SysNode):
    type: SysNodeType = SysNodeType.folder

class SysFile(SysNode):
    type: SysNodeType = SysNodeType.file
    size: str
    mime: Optional[str]