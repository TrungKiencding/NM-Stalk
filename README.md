# NetMind Stalk - AI News Aggregator and Analyzer

An intelligent system that crawls, analyzes, and synthesizes AI-related news and research from multiple sources including GitHub, arXiv, and Facebook.

## 🌟 Features

- **Multi-Source Data Collection**
  - GitHub trending AI repositories
  - Latest arXiv AI research papers
  - AI-related Facebook posts
  - Smart duplicate detection and filtering

- **Intelligent Content Processing**
  - Automatic content tagging and categorization
  - Advanced text summarization
  - Smart title generation
  - Quality inspection and validation

- **Content Synthesis**
  - Related content grouping using semantic analysis
  - Automated research synthesis
  - Cross-source relationship analysis

- **Web Interface**
  - Clean, responsive dashboard
  - Date-based content filtering
  - Source-based content filtering
  - Real-time content updates

- **Monitoring & Analytics**
  - Prometheus metrics integration
  - Grafana dashboards
  - Performance monitoring
  - System health checks

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- PostgreSQL 13+
- Python 3.11+
- API keys for:
  - Azure OpenAI
  - Voyage AI
  - Google Search API (optional)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd netmind-stalk
```

2. **Set up environment variables:**
Create a `.env` file with:
```bash
# Azure OpenAI Settings
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment>

# Voyage AI Settings
VOYAGE_API_KEY=<your-key>

# Database Settings
DB_USER=<user>
DB_PASSWORD=<password>
DB_HOST=db
DB_PORT=5432
DB_NAME=netmind_stalk

# Optional: Google Search Settings
GOOGLE_SEARCH_API_KEY=<your-key>
GOOGLE_SEARCH_ENGINE_ID=<your-engine-id>

# Optional: Facebook Settings
FACEBOOK_EMAIL=<your-email>
FACEBOOK_PASSWORD=<your-password>
FACEBOOK_PAGES=<comma-separated-urls>
```

3. **Start the services:**
```bash
docker-compose up -d
```

## 🔧 Usage

### Web Interface
Access the web dashboard at `http://localhost:5000`

### Manual Data Collection
```bash
python main.py
```

### Database Management
```bash
# View database summary
python scripts/db_summary.py

# Clear database
python scripts/clear_database.py
```

### Monitoring
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## 🏗️ Architecture

```
netmind-stalk/
├── agents/          # AI agents for different tasks
├── crawlers/        # Source-specific data collectors
├── models/          # Database models and schemas
├── services/        # Business logic services
├── templates/       # Web interface templates
├── tools/          # Utility tools
└── utils/          # Helper functions
```

## 🔍 Key Components

- **Research Crawler**: Collects data from multiple sources
- **Content Processor**: Cleans and processes raw content
- **Semantic Analyzer**: Groups related content
- **Synthesis Service**: Generates research summaries
- **Web Interface**: Presents processed content

## 📊 Monitoring

The system includes comprehensive monitoring:
- API request metrics
- Database performance
- System resource usage
- Error rates and types

## 🛠️ Development

1. Create virtual environment:
```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
playwright install-deps
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.