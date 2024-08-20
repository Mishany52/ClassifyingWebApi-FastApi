from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.website import WebSite, WebSiteCreate, WebSiteSearchResults, WebSiteUpdate
from app import services
from app import deps
from app.config import settings

from pydantic import AnyUrl

webSiteRouter = r = APIRouter()


@r.post(
    '/webSites/', response_model=WebSite
)
async def create(
        *,
        webSite_in: WebSiteCreate,
        db: Session = Depends(deps.get_db),
) -> dict:
    """
    Add a new webSite
    """
    webSites = await services.webSite.create(db=db, obj_in=webSite_in)
    return webSites


@r.get(
    '/webSites/{website_id}', status_code=200, response_model=WebSite
)
async def get(
        *,
        website_id: int,
        db: Session = Depends(deps.get_db),
) -> Any:
    result = await services.webSite.get(db=db, id=website_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"WebSite with ID {website_id} not found")
    return result


@r.get(
    "/websites/", status_code=200, response_model=WebSiteSearchResults
)
async def getMulti(
        *,
        db: Session = Depends(deps.get_db),
) -> dict:
    webSites = await services.webSite.get_multi(db=db, limit=20)
    return {"results": list(webSites)}


@r.get(
    "/website/search/", status_code=200,
    response_model=WebSiteSearchResults
)
async def search(
        *,
        webSiteUrl: Optional[str] = Query(None, min_length=1, example="vk.com"),
        max_results: Optional[int] = 10,
        db: Session = Depends(deps.get_db),
) -> dict:
    webSites = await services.webSite.get_multi(db=db, limit=max_results)
    if not webSiteUrl:
        return {'result', webSites}
    results = filter(lambda website: webSiteUrl.lower() in website.url.lower(), webSites)
    return {"results": list(results)[:max_results]}


@r.put(
    "/website/{website_id}", status_code=200, response_model=WebSite
)
async def update(
        *,
        website_id: int,
        db: Session = Depends(deps.get_db),
        update_data: WebSiteUpdate,
) -> Any:
    result = await services.webSite.update(db=db, id=website_id, obj_in=update_data)
    return result


@r.delete(
    "/website/{website_id}", status_code=200, response_model=WebSite
)
async def remove(
        *,
        website_id: int,
        db: Session = Depends(deps.get_db)
) -> Any:
    result = await services.webSite.remove(db=db, id=website_id)
    return result


@r.post(
    "/website/editCSVandSave", status_code=200
)
async def editCSVandSave(
        *,
        fileName: str = settings.DATASET_PATH_SERVER,
):
    df = services.webSite.editCSVandSave(fileName=fileName)
    return df


@r.post(
    "/website/uploadCVStoDB", status_code=200
)
async def uploadCVStoDB(
        *,
        db: Session = Depends(deps.get_db),
        fileName: str = settings.PDATASET_PATH_SERVER,
):
    df = await services.webSite.uploadCSVtoDB(db=db, fileName=fileName)
    return df


@r.get("/website/preparedText/")
async def parsAndPreparedText(
        *,
        url: AnyUrl,
):
    preparedText = services.webSite.getPreparedTextByUrl(url=url, headers=settings.HEADERS)
    return preparedText


