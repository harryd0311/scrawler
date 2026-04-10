from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    summary: Optional[str] = None
    source: str
    category: str
    published_date: date
    is_starred: bool
    score: int
    crawled_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    total: int
    starred: int
    today: int
    by_category: dict
