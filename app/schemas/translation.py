from typing import Optional
from pydantic import BaseModel


class TextSchema(BaseModel):
    text: Optional[str]
