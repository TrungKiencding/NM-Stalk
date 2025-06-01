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
    title: str
    content_snippet: str
    publication_date: datetime
    cleaned_text: Optional[str] = None
    content_tags: Optional[List[str]] = None
    source_tags: Optional[List[str]] = None
    embedding: Optional[List[float]] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None
    is_novel: Optional[bool] = None
    summary: Optional[str] = None
    news_snippet: Optional[str] = None
    is_final_selection: Optional[bool] = None

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
    source_tags = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    source = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=True)
    is_novel = Column(Boolean, nullable=True)
    summary = Column(String, nullable=True)
    news_snippet = Column(String, nullable=True)
    is_final_selection = Column(Boolean, nullable=True)

    def to_item(self) -> Item:
        return Item(
            id=self.id,
            url=self.url,
            title=self.title,
            content_snippet=self.content_snippet,
            publication_date=self.publication_date,
            cleaned_text=self.cleaned_text,
            content_tags=self.content_tags,
            source_tags=self.source_tags,
            embedding=self.embedding,
            source=self.source,
            timestamp=self.timestamp,
            is_novel=self.is_novel,
            summary=self.summary,
            news_snippet=self.news_snippet,
            is_final_selection=self.is_final_selection
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
            source_tags=item.source_tags,
            embedding=item.embedding,
            source=item.source,
            timestamp=item.timestamp,
            is_novel=item.is_novel,
            summary=item.summary,
            news_snippet=item.news_snippet,
            is_final_selection=item.is_final_selection
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
