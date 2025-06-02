from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Pydantic Models for API/Data Transfer
class Item(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    content_snippet: str
    publication_date: datetime
    cleaned_text: Optional[str] = None
    content_tags: Optional[List[str]] = None
    source: Optional[str] = None
    embedding: Optional[List[float]] = None
    timestamp: Optional[datetime] = None
    summary: Optional[str] = None
    news_snippet: Optional[str] = None


class SynthesizedArticle(BaseModel):
    tag: str
    article: str
    date: datetime

class State(BaseModel):
    session_count: int = 0
    items: List[Item] = []
    synthesized_articles: List[SynthesizedArticle] = []

# SQLAlchemy Models for Database
class DBItem(Base):
    __tablename__ = 'items'
    
    id = Column(String, primary_key=True)
    url = Column(String)
    title = Column(String)
    content_snippet = Column(String)
    publication_date = Column(DateTime)
    cleaned_text = Column(String, nullable=True)    
    content_tags = Column(JSON, nullable=True)
    source = Column(String, nullable=True)
    embedding = Column(JSON, nullable=True)  
    timestamp = Column(DateTime, nullable=True)
    summary = Column(String, nullable=True)
    news_snippet = Column(String, nullable=True)

    def to_item(self) -> Item:
        return Item(
            id=self.id,
            url=self.url,
            title=self.title,
            content_snippet=self.content_snippet,
            publication_date=self.publication_date,
            cleaned_text=self.cleaned_text,
            content_tags=self.content_tags,
            source=self.source,
            embedding=self.embedding,
            timestamp=self.timestamp,
            summary=self.summary,
            news_snippet=self.news_snippet,
        )

    @classmethod
    def from_item(cls, item: Item) -> 'DBItem':
        return cls(
            id=item.id,
            url=item.url,
            title=item.title,
            content_snippet=item.content_snippet,
            publication_date=item.publication_date,
            cleaned_text=item.cleaned_text,
            content_tags=item.content_tags,
            source=item.source,
            embedding=item.embedding,
            timestamp=item.timestamp,
            summary=item.summary,
            news_snippet=item.news_snippet,
        )

class DBArticle(Base):
    __tablename__ = 'synthesized_articles'
    
    id = Column(String, primary_key=True)
    tag = Column(String)
    article = Column(String)
    date = Column(DateTime)

    def to_article(self) -> SynthesizedArticle:
        return SynthesizedArticle(
            tag=self.tag,
            article=self.article,
            date=self.date
        )

    @classmethod
    def from_article(cls, article: SynthesizedArticle, id: str) -> 'DBArticle':
        return cls(
            id=id,
            tag=article.tag,
            article=article.article,
            date=article.date
        )
