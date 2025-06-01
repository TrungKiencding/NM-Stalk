# NetMind Stalk

A news aggregation and analysis system that collects, processes, and synthesizes news articles using AI.

## Features

- News article collection and processing
- Content analysis and tagging
- Article synthesis and summarization
- Database management for storing articles and metadata
- Reporting functionality for database insights

## Requirements

- Python 3.8+
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

## Usage

1. Database Summary:
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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
