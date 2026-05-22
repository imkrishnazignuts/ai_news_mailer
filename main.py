from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from llm_service import router as llm_router
from fastapi import FastAPI
from all_articles import router as all_article_router
from new_article_retrival import router as new_article_router
from database import engine
from models import Base
from fastapi_pagination import Page, add_pagination, paginate

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    lifespan=lifespan
)

add_pagination(app)
app.include_router(all_article_router)
app.include_router(new_article_router)
app.include_router(llm_router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def home():
    return FileResponse("frontend/index.html")