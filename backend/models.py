from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime
from sqlalchemy.sql import func
from database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    summary = Column(Text)
    source = Column(String(100))
    category = Column(String(50))  # AI, WebDev, SpringBoot, AWS, Azure, DevOps, General
    published_date = Column(Date, nullable=False, index=True)
    crawled_at = Column(DateTime, server_default=func.now())
    is_starred = Column(Boolean, default=False, nullable=False)
    score = Column(Integer, default=0)
