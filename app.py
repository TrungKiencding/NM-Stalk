from flask import Flask, render_template, jsonify
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from models.models import DBItem, DBArticle
from sqlalchemy.orm import sessionmaker
import markdown2
from config import Config

app = Flask(__name__)

# Database setup
engine = create_engine(Config.get_database_url())
Session = sessionmaker(bind=engine)

def clean_markdown(text):
    """Clean markdown text for proper HTML rendering"""
    if not text:
        return ""
    # Convert markdown to HTML
    html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables'])
    return html

def format_tags(tags):
    """Format tags list into markdown style tags"""
    if not tags:
        return []
    return [f"#{tag}" for tag in tags]

def format_related_content(related_content):
    """Format related content for display"""
    if not related_content:
        return []
    
    # Only include content that has been successfully enriched
    filtered_content = [
        content for content in related_content 
        if content.get('raw_content') and 
        content['raw_content'] != '[FAILED to crawl]' and
        not any(skip_text in content['link'].lower() for skip_text in [
            'table of contents',
            'skip to main content',
            'abstract',
            '/html/',
            '/abs/'
        ])
    ]
    
    return [
        {
            'link': content['link'],
            'raw_content': clean_markdown(content['raw_content'])
        }
        for content in filtered_content
    ]

def get_source_from_url(url):
    """Determine the source platform from the URL"""
    url_lower = url.lower()
    if 'facebook.com' in url_lower:
        return 'facebook'
    elif 'github.com' in url_lower:
        return 'github'
    elif 'arxiv.org' in url_lower:
        return 'arxiv'
    return 'other'

def get_news_data(selected_date=None):
    session = Session()
    try:
        # Query all items ordered by timestamp
        query = session.query(DBItem).order_by(DBItem.timestamp.desc())
        
        # If date is provided, filter by date
        if selected_date:
            query = query.filter(
                DBItem.timestamp >= selected_date.replace(hour=0, minute=0, second=0),
                DBItem.timestamp < selected_date.replace(hour=23, minute=59, second=59)
            )
        
        items = query.all()
        return items
    finally:
        session.close()

def get_synthesized_articles(selected_date=None):
    session = Session()
    try:
        # Query all synthesized articles ordered by date
        query = session.query(DBArticle).order_by(DBArticle.date.desc())
        
        # If date is provided, filter by date
        if selected_date:
            query = query.filter(
                DBArticle.date >= selected_date.replace(hour=0, minute=0, second=0),
                DBArticle.date < selected_date.replace(hour=23, minute=59, second=59)
            )
        
        articles = query.all()
        return articles
    finally:
        session.close()

@app.route('/')
def index():
    # Get today's news
    today = datetime.today()
    news_items = get_news_data(today)
    synthesized_articles = get_synthesized_articles(today)
    
    # Process each news item
    processed_items = []
    for item in news_items:
        processed_item = {
            'id': item.id,
            'title': clean_markdown(item.title),
            'news_snippet': clean_markdown(item.news_snippet),
            'timestamp': item.timestamp,
            'url': item.url,
            'content_tags': format_tags(item.content_tags),
            'related_content': format_related_content(item.related_content),
            'source': get_source_from_url(item.url)
        }
        processed_items.append(processed_item)
    
    # Process synthesized articles
    processed_articles = []
    for article in synthesized_articles:
        processed_article = {
            'id': article.id,
            'tag': article.tag,
            'article': clean_markdown(article.article),
            'date': article.date
        }
        processed_articles.append(processed_article)
    
    return render_template(
        'index.html',
        news_items=processed_items,
        synthesized_articles=processed_articles,
        selected_date=today.strftime('%Y-%m-%d')
    )

@app.route('/api/news/<date>')
def get_news(date):
    try:
        selected_date = datetime.strptime(date, '%Y-%m-%d')
        news_items = get_news_data(selected_date)
        synthesized_articles = get_synthesized_articles(selected_date)
        
        # Convert to dictionary for JSON response
        news_data = [{
            'id': item.id,
            'title': clean_markdown(item.title),
            'news_snippet': clean_markdown(item.news_snippet),
            'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'url': item.url,
            'content_tags': format_tags(item.content_tags),
            'related_content': format_related_content(item.related_content),
            'source': get_source_from_url(item.url)
        } for item in news_items]
        
        # Convert synthesized articles to dictionary
        articles_data = [{
            'id': article.id,
            'tag': article.tag,
            'article': clean_markdown(article.article),
            'date': article.date.strftime('%Y-%m-%d %H:%M:%S')
        } for article in synthesized_articles]
        
        return jsonify({
            'status': 'success',
            'count': len(news_data),
            'data': news_data,
            'synthesized_articles': articles_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=5000) 