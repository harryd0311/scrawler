from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db
from scheduler import start_scheduler

models.Base.metadata.create_all(bind=engine)

_scheduler = None
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    _scheduler = start_scheduler()
    yield
    if _scheduler:
        _scheduler.shutdown(wait=False)


app = FastAPI(title="TechNews Daily", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve built React frontend (production)
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/api/articles", response_model=List[schemas.ArticleResponse])
def get_articles(
    date_filter: Optional[str] = Query(None, description="YYYY-MM-DD"),
    days: Optional[int] = Query(None, description="Last N days"),
    category: Optional[str] = Query(None),
    starred: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(models.Article)

    if date_filter:
        q = q.filter(models.Article.published_date == date_filter)
    elif days:
        since = date.today() - timedelta(days=days)
        q = q.filter(models.Article.published_date >= since)

    if category and category != "All":
        q = q.filter(models.Article.category == category)

    if starred is not None:
        q = q.filter(models.Article.is_starred == starred)

    return (
        q.order_by(
            models.Article.published_date.desc(),
            models.Article.score.desc(),
        )
        .limit(200)
        .all()
    )


@app.patch("/api/articles/{article_id}/star")
def toggle_star(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.is_starred = not article.is_starred
    db.commit()
    return {"id": article_id, "is_starred": article.is_starred}


@app.post("/api/crawl")
def trigger_crawl(db: Session = Depends(get_db)):
    from crawler import run_all_crawlers

    count = run_all_crawlers(db)
    return {"message": f"Crawled {count} new articles"}


@app.get("/api/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(models.Article.id)).scalar() or 0
    starred = (
        db.query(func.count(models.Article.id))
        .filter(models.Article.is_starred == True)
        .scalar()
        or 0
    )
    today_count = (
        db.query(func.count(models.Article.id))
        .filter(models.Article.published_date == date.today())
        .scalar()
        or 0
    )
    by_category = {
        cat: cnt
        for cat, cnt in db.query(
            models.Article.category, func.count(models.Article.id)
        ).group_by(models.Article.category).all()
    }
    return {"total": total, "starred": starred, "today": today_count, "by_category": by_category}


# Catch-all: serve React app for any non-API route (must be last)
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"detail": "Frontend not built. Run: cd frontend && npm run build"}
