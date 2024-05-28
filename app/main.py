from fastapi import FastAPI, Request, Depends

from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from app.db.init_db import init_db
from app.router.website import webSiteRouter
from app.router.translation import translationRouter
from app.config import settings
from app import deps

from app.schemas.classification import ClassRequest
from app.classifier.bertModel.RoBERTa_classifier import get_model, RoBERTaClassifier
app = FastAPI(title=settings.PROJECT_NAME, docs_url="/api/docs")


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/api/v1", status_code=200)
async def root(
        request: Request,
        db: AsyncSession = Depends(deps.get_db),
):
    return {"message": "Hello World"}

@app.post("/predict")
def predict(request: ClassRequest, model: RoBERTaClassifier = Depends(get_model)):
    predict = model.predict(request.text)
    return predict

# Routers
app.include_router(
    webSiteRouter,
    prefix="/api/v1",
    tags=["webSites"],
)
app.include_router(
    translationRouter,
    prefix="/api/v1",
    tags=["translate"],
)
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", reload=True, port=8888, log_level="debug")
