# SearchEngine Pro - Quick Start Guide

Welcome to SearchEngine Pro! This guide will help you get started quickly.

## 🚀 Quick Installation

1. **Clone or download the project**
   ```bash
   # If you have the project files
   cd SearchEnginePro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the installation**
   ```bash
   python test_installation.py
   ```

## 🎯 Running the Search Engine

### Interactive Mode (Default)
```bash
python run_search_engine.py
```

This will start the interactive console where you can:
- Type search queries directly
- Use navigation commands (n, p, o #)
- Access search history (h)
- Apply filters (f)
- Get help (?)

### Single Query Mode
```bash
python run_search_engine.py -q "python programming"
```

### Batch Mode
```bash
python run_search_engine.py --batch examples/example_queries.txt
```

## 📖 Basic Commands

Once in interactive mode, you can use these commands:

### Search Commands
- `python tutorial` - Search for Python tutorials
- `"machine learning"` - Search for exact phrase
- `python +tutorial` - Require "tutorial" in results
- `python -snake` - Exclude "snake" from results
- `site:github.com python` - Search only on GitHub

### Navigation
- `n` or `next` - Next page of results
- `p` or `prev` - Previous page
- `o 1` - Open result #1
- `back` - Return to previous results

### Tools
- `h` or `history` - Show search history
- `f` or `filter` - Show/modify filters
- `s` or `save` - Save current search
- `bookmarks` - Show bookmarks

### Interface
- `c` or `clear` - Clear screen
- `r` or `refresh` - Refresh search
- `?` or `help` - Show help
- `exit` or `quit` - Exit application

## 🔧 Configuration

The search engine creates a configuration file at:
- **Linux/Mac**: `~/.config/searchengine/config.yaml` (or `~/.searchengine/config.yaml` if permission issues)
- **Windows**: `%APPDATA%\searchengine\config.yaml`

You can customize:
- Results per page
- Display settings
- Cache settings
- Search providers

## 📝 Example Session

```
╔══════════════════════════════════════════════════════════════╗
║                    SearchEngine Pro v3.2                    ║
║                  Interactive Console Mode                    ║
╚══════════════════════════════════════════════════════════════╝

Ready for search queries and commands.
Type '?' for help or start typing your search...

> python programming tutorial

Searching...................... 100%

Found 2,847,000 results (0.34 seconds)
Showing results 1-10:

1. Python.org - Welcome to Python.org
   https://www.python.org/
   The official home of the Python Programming Language...
   python.org

2. Python Tutorial - W3Schools
   https://www.w3schools.com/python/
   Well organized tutorials with examples...
   w3schools.com

Page 1 of 284,700 | Commands: n=next, p=prev, o#=open, f=filter, ?=help
> o 1

📖 Opening: Python.org - Welcome to Python.org
🔗 URL: https://www.python.org/
📄 The official home of the Python Programming Language...

[Result opened in browser simulation]

> exit

Thank you for using SearchEngine Pro!
Session ended.
```

## 🆘 Troubleshooting

### Import Errors
If you get import errors, make sure you've installed the dependencies:
```bash
pip install -r requirements.txt
```

### Missing Dependencies
The main dependencies are:
- `rich` - For beautiful console output
- `click` - For command-line interface
- `pyyaml` - For configuration files

### Permission Issues
If you get permission errors, try:
```bash
python3 run_search_engine.py
```

## 🎉 You're Ready!

That's it! You now have a fully functional console-based search engine. 

For more advanced features and configuration options, check out the full README.md file.

Happy searching! 🔍 