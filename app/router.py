from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas.website import WebSite, WebSiteCreate
from app import crud
from app import deps
webSiteRouter = r = APIRouter()

@r.post('/webSites', response_model=WebSite)
async def add(*, webSite_in: WebSiteCreate, db:Session=Depends(deps.get_db)) -> dict:
    """
    Add a new webSite
    """
    webSite = crud.webSite.create(db=db, obj_in=webSite_in)
    return webSite