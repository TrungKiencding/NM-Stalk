# NetMind Stalk


## Features

- News article collection and processing
- Content analysis and tagging
- Article synthesis and summarization
- Database management for storing articles and metadata
- Reporting functionality for database insights

## Requirements

- SQLite
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

## Enable Azure key
1. Make sure your .env file has the following configurations:
```bash
AZURE_OPENAI_ENDPOINT= ''
AZURE_OPENAI_API_KEY= ''
AZURE_OPENAI_API_VERSION = ''
VOYAGE_API_KEY = ''
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
├── db.sqlite        # SQLite database
└── README.md        # This file
```

