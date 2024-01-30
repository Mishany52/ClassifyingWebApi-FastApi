from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from sqlalchemy.orm import Session
import uvicorn


from app.router import webSiteRouter
from app.config import settings 
from app import deps
app = FastAPI(title=settings.PROJECT_NAME, docs_url="/api/docs")

@app.get("/api/v1", status_code=200)
async def root(
    request: Request,
    db: Session = Depends(deps.get_db),
):
    
    return {"message": "Hello World"}

#Routers
app.include_router(
    webSiteRouter,
    prefix="/api/v1",
    tags=["webSites"],
)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", reload=True, port=8888, log_level="debug")
