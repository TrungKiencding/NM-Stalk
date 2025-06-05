from flask import Flask, render_template, jsonify
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from models.models import DBItem
from sqlalchemy.orm import sessionmaker
import markdown2
import re

app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///db.sqlite')
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

@app.route('/')
def index():
    # Get today's news
    today = datetime.today()
    news_items = get_news_data(today)
    
    # Process each news item
    processed_items = []
    for item in news_items:
        processed_item = {
            'id': item.id,
            'title': clean_markdown(item.title),
            'news_snippet': clean_markdown(item.news_snippet),
            'timestamp': item.timestamp,
            'url': item.url,
            'content_tags': format_tags(item.content_tags)
        }
        processed_items.append(processed_item)
    
    return render_template(
        'index.html',
        news_items=processed_items,
        selected_date=today.strftime('%Y-%m-%d')
    )

@app.route('/api/news/<date>')
def get_news(date):
    try:
        selected_date = datetime.strptime(date, '%Y-%m-%d')
        news_items = get_news_data(selected_date)
        
        # Convert to dictionary for JSON response
        news_data = [{
            'id': item.id,
            'title': clean_markdown(item.title),
            'news_snippet': clean_markdown(item.news_snippet),
            'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'url': item.url,
            'content_tags': format_tags(item.content_tags)
        } for item in news_items]
        
        return jsonify({
            'status': 'success',
            'count': len(news_data),
            'data': news_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=5000) 