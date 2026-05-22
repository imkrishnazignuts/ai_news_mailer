from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import get_db
from models import NewsArticle
from fastapi_pagination import Page,paginate
from pydantic import BaseModel
from datetime import date



class newsArticle(BaseModel):
    id: int
    title: str
    url: str
    source: str
    summary: str
    published_at: str



router = APIRouter(
    prefix="/all-article",
    tags=["all articles"]
)

@router.get('')
def get_all_articles(db:Session=Depends(get_db)) ->Page[newsArticle] :
    return paginate(db.query(NewsArticle).all())
    


