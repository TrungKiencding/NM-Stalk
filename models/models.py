from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class RelatedContent(BaseModel):
    link: str
    raw_content: str

# Pydantic Models for API/Data Transfer
class Item(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    title: Optional[str] = None
    content_snippet: str
    publication_date: Optional[datetime] = None
    cleaned_text: Optional[str] = None
    content_tags: Optional[List[str]] = Field(default_factory=list)
    source: Optional[str] = None
    embedding: Optional[List[float]] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    summary: Optional[str] = None
    news_snippet: Optional[str] = None
    related_content: Optional[List[RelatedContent]] = Field(default_factory=list)

class SynthesizedArticle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tag: str
    article: str
    date: datetime = Field(default_factory=datetime.now)

class State(BaseModel):
    session_count: int = 1
    items: List[Item] = Field(default_factory=list)
    synthesized_articles: List[SynthesizedArticle] = Field(default_factory=list)
    inspection_results: List[Dict[str, Any]] = Field(default_factory=list)
    next_step: Optional[str] = None

# SQLAlchemy Models for Database
class DBItem(Base):
    __tablename__ = 'items'
    
    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    content_snippet = Column(String, nullable=False)
    publication_date = Column(DateTime, nullable=True)
    cleaned_text = Column(String, nullable=True)    
    content_tags = Column(JSON, nullable=True)
    source = Column(String, nullable=True)
    embedding = Column(JSON, nullable=True)  
    timestamp = Column(DateTime, nullable=True)
    summary = Column(String, nullable=True)
    news_snippet = Column(String, nullable=True)
    related_content = Column(JSON, nullable=True)

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
            related_content=[RelatedContent(**content) for content in (self.related_content or [])]
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
            related_content=[content.dict() for content in (item.related_content or [])]
        )

class DBArticle(Base):
    __tablename__ = 'synthesized_articles'
    
    id = Column(String, primary_key=True)
    tag = Column(String, nullable=False)
    article = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)

    def to_article(self) -> SynthesizedArticle:
        return SynthesizedArticle(
            id=self.id,
            tag=self.tag,
            article=self.article,
            date=self.date
        )

    @classmethod
    def from_article(cls, article: SynthesizedArticle) -> 'DBArticle':
        return cls(
            id=article.id,
            tag=article.tag,
            article=article.article,
            date=article.date
        )
