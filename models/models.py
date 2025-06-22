from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

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
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    summary: Optional[str] = None
    news_snippet: Optional[str] = None

class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None
    content_snippet: str
    publication_date: Optional[datetime] = None
    cleaned_text: Optional[str] = None
    source: Optional[str] = None

class HotTopic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    snippet: Optional[str] = None
    publication_date: Optional[datetime] = None

class State(BaseModel):
    session_count: int = 1
    items: List[Item] = Field(default_factory=list)
    posts: List[Post] = Field(default_factory=list)   
    inspection_results: List[Dict[str, Any]] = Field(default_factory=list)
    hot_topics: List[HotTopic] = Field(default_factory=list)
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
    timestamp = Column(DateTime, nullable=True)
    summary = Column(String, nullable=True)
    news_snippet = Column(String, nullable=True)
    source = Column(String, nullable=True)
    def to_item(self) -> Item:
        return Item(
            id=self.id,
            url=self.url,
            title=self.title,
            content_snippet=self.content_snippet,
            publication_date=self.publication_date,
            cleaned_text=self.cleaned_text,
            content_tags=self.content_tags,
            timestamp=self.timestamp,
            summary=self.summary,
            news_snippet=self.news_snippet,
            source=self.source,
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
            timestamp=item.timestamp,
            summary=item.summary,
            news_snippet=item.news_snippet,
            source=item.source,
        )


class DBPost(Base):
    __tablename__ = 'posts'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=True)
    content_snippet = Column(String, nullable=False)
    publication_date = Column(DateTime, nullable=True)
    cleaned_text = Column(String, nullable=True)
    source = Column(String, nullable=True)

    def to_post(self) -> Post:
        return Post(
            id=self.id,
            title=self.title,
            content_snippet=self.content_snippet,
            publication_date=self.publication_date,
            cleaned_text=self.cleaned_text,
            source=self.source,
        )

    @classmethod
    def from_post(cls, post: Post) -> 'DBPost':
        return cls(
            id=post.id,
            title=post.title,
            content_snippet=post.content_snippet,
            publication_date=post.publication_date,
            cleaned_text=post.cleaned_text,
            source=post.source,
        )

class DBHotTopic(Base):
    __tablename__ = 'hot_topics'
    
    id = Column(String, primary_key=True)
    snippet = Column(String, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    
    def to_hot_topic(self) -> HotTopic:
        return HotTopic(
            id=self.id,
            snippet=self.snippet,
            publication_date=self.publication_date,
        )

    @classmethod
    def from_hot_topic(cls, hot_topic: HotTopic) -> 'DBHotTopic':
        return cls(
            id=hot_topic.id,
            snippet=hot_topic.snippet,
            publication_date=hot_topic.publication_date,
        )