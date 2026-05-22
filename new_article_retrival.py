from fastapi import APIRouter,Depends
from rss_feed_data import fetch_news
from sqlalchemy.orm import Session
from database import get_db
from models import NewsArticle

router = APIRouter(
    prefix="/new-article",
    tags=["new articles"]
)

@router.get("")
def get_new_articles(db: Session = Depends(get_db)):
    fetched_articles = fetch_news()
    new_articles = []

    for article in fetched_articles:
        exists = db.query(NewsArticle).filter(
            NewsArticle.url == article["url"]
        ).first()

        if exists:
            continue

        new_article = NewsArticle(
            title=article.get("title", ""),
            url=article.get("url", ""),
            source=article.get("source"),
            summary=article.get("summary"),
            published_at=article.get("published"),
            is_sent=False
        )

        db.add(new_article)
        db.commit()
        db.refresh(new_article)

        new_articles.append({
            "id": new_article.id,
            "title": new_article.title,
            "url": new_article.url,
            "source": new_article.source,
            "summary": new_article.summary,
            "published_at": new_article.published_at,
            "fetched_at": new_article.fetched_at,
            "is_sent": new_article.is_sent
        })

    return new_articles

