from typing import Any, Optional, Dict, List
from fastapi import APIRouter, Request, Depends,HTTPException, Query
from sqlalchemy.orm import Session
from app import deps
from app.schemas import TextSchema
from app import services
translationRouter = r = APIRouter()

@r.post(
    '/translation/',
)
async def translate(
    *,
    preparedText: TextSchema,
) -> str:
    """
    Add a new webSite
    """
    result = services.translator.translateIntoEn(preparedText.text)
    return result
