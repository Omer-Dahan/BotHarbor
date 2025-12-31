# BotHarbor

Windows desktop manager for running multiple Python Telegram bots with strong logging, persistent configuration, and a modern UI.

## Features

- **Project Management**: Add, start, stop, and monitor multiple Python bot projects
- **Real-time Logging**: Capture and persist stdout/stderr from running bots
- **Modern Dark UI**: Clean PySide6 interface with dark theme
- **Persistent Configuration**: SQLite database for project storage

## Requirements

- Python 3.10+
- Windows 10/11

## Installation

```bash
# Clone or download the repository
cd BotHarbor

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
# From project root with venv activated
python -m botharbor.main
```

## Project Structure

```
BotHarbor/
├── src/botharbor/      # Main package
│   ├── core/           # Process management, logging
│   ├── database/       # SQLAlchemy models and CRUD
│   ├── ui/             # PySide6 UI components
│   └── utils/          # Helper utilities
├── data/               # Runtime data (logs, database)
└── requirements.txt
```

## License

MIT
