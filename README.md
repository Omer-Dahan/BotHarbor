# H.A.M.A.L
**Python Bot Management Made Easy**

**H.A.M.A.L** (Command Center) is a Windows desktop application provided for **Israel's 75th** - "Hamal". It allows you to manage multiple Python scripts (Telegram bots, scrapers, etc.) from a single, modern interface.

<p align="center">
  <img src="https://raw.githubusercontent.com/Omer-Dahan/HAMAL/main/docs/screenshot.png" alt="H.A.M.A.L Screenshot" width="800">
</p>

## ✨ Features
- 🚀 **Process Management**: Start, stop, and restart scripts with one click.
- 📊 **Real-time Monitoring**: View uptime and status (Running/Stopped/Crashed) for each bot.
- 📝 **Log Viewer**: Live log streaming for each process, with automatic file logging.
- 🎨 **Modern UI**: Beautiful, dark-themed interface built with CustomTkinter.
- 🛡️ **Isolation**: Runs each script in its own process, ensuring one crash doesn't affect others.
- 💾 **Persistence**: Remembers your project list and settings.

## 📦 Installation
Download the latest installer from the [Releases](https://github.com/Omer-Dahan/HAMAL/releases) page.

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+
- Poetry (recommended) or pip

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/Omer-Dahan/HAMAL.git
   cd HAMAL
   ```
2. Create virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python -m hamal.main
   ```

## 🏗️ Project Structure
```text
HAMAL/
├── src/hamal/      # Main package
│   ├── core/       # Core logic (ProcessManager, Config)
│   ├── database/   # Database models and CRUD
│   ├── ui/             # PySide6 UI components
│   └── utils/          # Helper utilities
├── data/               # Runtime data (logs, database)
└── requirements.txt
```

## License

MIT
