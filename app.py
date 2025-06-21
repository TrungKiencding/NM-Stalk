from flask import Flask, render_template, jsonify, Response
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from models.models import DBItem, DBArticle
from sqlalchemy.orm import sessionmaker
import markdown2
from config import Config
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# Database setup
engine = create_engine(
    Config.get_database_url(),
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,  # Add connection health check
    pool_recycle=3600    # Recycle connections after 1 hour
)
Session = sessionmaker(bind=engine)

# Add these metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

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
    elif 'x.com' in url_lower:
        return 'x'
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

def process_item(item):
    """Process a single news item for display"""
    return {
        'id': item.id,
        'title': clean_markdown(item.title),
        'news_snippet': clean_markdown(item.news_snippet),
        'timestamp': item.timestamp,
        'url': item.url,
        'content_tags': format_tags(item.content_tags),
        'related_content': format_related_content(item.related_content),
        'source': get_source_from_url(item.url)
    }

def process_article(article):
    """Process a single synthesized article for display"""
    return {
        'id': article.id,
        'tag': article.tag,
        'article': clean_markdown(article.article),
        'date': article.date
    }

@app.route('/')
def index():
    # Get today's news
    today = datetime.today()
    news_items = get_news_data(today)
    synthesized_articles = get_synthesized_articles(today)
    
    # Process items and articles
    processed_items = [process_item(item) for item in news_items]
    processed_articles = [process_article(article) for article in synthesized_articles]
    
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
        
        # Process items and articles
        news_data = [process_item(item) for item in news_items]
        articles_data = [process_article(article) for article in synthesized_articles]
        
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

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

def track_metrics(f):
    def wrapped(*args, **kwargs):
        REQUEST_COUNT.inc()
        with REQUEST_LATENCY.time():
            return f(*args, **kwargs)
    return wrapped

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000) 

@app.route('/health')
def health_check():
    try:
        # Verify database connection
        with Session() as session:
            session.execute('SELECT 1')
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500