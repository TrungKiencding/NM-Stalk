# NetMind Stalk


## Features

- News article collection and processing
- Content analysis and tagging
- Article synthesis and summarization
- Database management for storing articles and metadata
- Reporting functionality for database insights

## Requirements

- PostgreSQL 14.0 or higher
- Required Python packages are listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NetMind-Stalk.git
cd NetMind-Stalk
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:
   - Install PostgreSQL if not already installed
   - Create a new database:
```bash
createdb netmind_stalk
```

5. Configure environment variables in .env file:
```bash
# Azure OpenAI Settings
AZURE_OPENAI_ENDPOINT=''
AZURE_OPENAI_API_KEY=''
AZURE_OPENAI_API_VERSION=''
VOYAGE_API_KEY=''

# Database Settings
DB_USER='postgres'
DB_PASSWORD='postgres'
DB_HOST='localhost'
DB_PORT='5432'
DB_NAME='netmind_stalk'
```

## Usage

1. Run test:
```bash
python main.py
```

2. Database Summary:
```bash
python scripts/db_summary.py
```

## Project Structure

```
NetMind-Stalk/
├── models/           # Database models and schemas
├── scripts/         # Utility scripts
└── README.md        # This file
```

