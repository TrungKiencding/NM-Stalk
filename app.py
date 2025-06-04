from flask import Flask, render_template, jsonify
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from models.models import DBItem
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///db.sqlite')
Session = sessionmaker(bind=engine)

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
    
    # Group news by hour
    news_by_hour = {}
    for item in news_items:
        hour = item.timestamp.hour
        if hour not in news_by_hour:
            news_by_hour[hour] = []
        news_by_hour[hour] = news_by_hour[hour] + [item]
    
    # Sort hours in reverse order
    sorted_hours = sorted(news_by_hour.keys(), reverse=True)
    
    return render_template(
        'index.html',
        news_by_hour=news_by_hour,
        sorted_hours=sorted_hours,
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
            'title': item.title,
            'news_snippet': item.news_snippet,
            'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'url': item.url,
            'content_tags': item.content_tags
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
    # Create templates directory and template file
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create the HTML template
    template = """
<!DOCTYPE html>
<html>
<head>
    <title>AI News Updates</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .news-item {
            margin-bottom: 1rem;
            padding: 1rem;
            border: 1px solid #dee2e6;
            border-radius: 0.25rem;
        }
        .time-block {
            background: #f8f9fa;
            padding: 0.5rem;
            margin: 1rem 0;
            border-radius: 0.25rem;
        }
        .realtime-clock {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            padding: 1rem;
            background: linear-gradient(45deg, #1e3799, #0c2461);
            color: white;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1 class="text-center mb-4">AI News Updates</h1>
        
        <div class="realtime-clock" id="clock"></div>
        
        <div class="row">
            <div class="col-md-3">
                <input type="date" class="form-control" id="dateSelector" value="{{ selected_date }}">
            </div>
        </div>

        <div id="newsContent">
            {% if news_by_hour %}
                {% for hour in sorted_hours %}
                    <div class="time-block">
                        <h3>{{ '%02d:00'|format(hour) }}</h3>
                        {% for item in news_by_hour[hour] %}
                            <div class="news-item">
                                <h4>{{ item.title }}</h4>
                                <p>{{ item.news_snippet }}</p>
                                {% if item.url %}
                                    <a href="{{ item.url }}" target="_blank" class="btn btn-sm btn-primary">Source</a>
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">No news articles found for this date.</div>
            {% endif %}
        </div>
    </div>

    <script>
        // Update clock
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').textContent = now.toLocaleTimeString();
        }
        setInterval(updateClock, 1000);
        updateClock();

        // Handle date selection
        document.getElementById('dateSelector').addEventListener('change', function(e) {
            fetch('/api/news/' + e.target.value)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        location.reload();
                    }
                });
        });
    </script>
</body>
</html>
    """
    
    with open('templates/index.html', 'w') as f:
        f.write(template)
    
    # Run the Flask app
    app.run(debug=True, port=5000) 