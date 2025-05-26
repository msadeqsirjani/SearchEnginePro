# SearchEngine Pro v3.2


**A comprehensive interactive console-based web search engine with advanced features and real-time search capabilities.**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/msadeqsirjani/SearchEnginePro)

## 🚀 Features

### Core Search Functionality
- **Real-time Web Search**: Perform live web searches with instant results
- **Multiple Search Types**: Web pages, news, images, academic papers, shopping
- **Advanced Query Processing**: Support for operators like `+`, `-`, `"exact phrases"`, `site:`
- **Intelligent Result Ranking**: Smart relevance scoring and result organization

### Interactive Console Interface
- **Rich Terminal UI**: Beautiful console interface with colors and formatting
- **Command-line Navigation**: Intuitive keyboard shortcuts and commands
- **Loading Animations**: Real-time feedback with ASCII progress indicators
- **Multi-page Results**: Seamless pagination through search results

### Advanced Features
- **Search History**: Track and revisit previous searches
- **Smart Filters**: Date range, content type, language, and region filtering
- **Bookmarking System**: Save and organize important search results
- **Session Management**: Persistent search state and preferences
- **Export Capabilities**: Save results in various formats
- **Safe Search**: Configurable content filtering

### Developer Features
- **Modular Architecture**: Clean, extensible codebase
- **API Integration**: Support for multiple search providers
- **Async Support**: High-performance asynchronous operations
- **Comprehensive Testing**: Full test suite with unit and integration tests
- **Rich Documentation**: Extensive docs and examples

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Install
```bash
# Clone the repository
git clone https://github.com/msadeqsirjani/SearchEnginePro.git
cd SearchEnginePro

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Development Setup
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## 🎯 Quick Start

### Basic Usage
```bash
# Start the search engine
searchengine

# Or use the shorter alias
sepro
```

### Example Session
```
╔══════════════════════════════════════════════════════════════╗
║                    SearchEngine Pro v3.2                     ║
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
   Official Site

2. Python Tutorial - W3Schools
   https://www.w3schools.com/python/
   Well organized tutorials with examples...
   Tutorial

[... more results ...]

Commands: n=next, p=prev, o#=open, f=filter, ?=help
>
```

## 🔧 Commands Reference

### Search Commands
| Command | Description | Example |
|---------|-------------|---------|
| `[query]` | Perform web search | `python tutorial` |
| `"exact phrase"` | Search exact phrase | `"machine learning"` |
| `term1 +term2` | Require term2 | `python +tutorial` |
| `term1 -term2` | Exclude term2 | `python -snake` |
| `site:domain.com` | Search specific site | `site:github.com` |

### Navigation & Pagination Commands
| Command | Description |
|---------|-------------|
| `n`, `next` | Next page of results |
| `p`, `prev` | Previous page of results |
| `first` | Jump to first page |
| `last` | Jump to last page |
| `page [#]` | Jump to specific page number |
| `o [#]`, `open [#]` | Open result number # |
| `back` | Return to previous results |

**🔄 Enhanced Pagination Features:**
- ✅ Real Google search pagination with proper page offsetting
- 📊 Dynamic page calculation based on total results  
- 🛡️ Smart validation prevents invalid page navigation
- ⚡ Fast loading with beautiful status indicators
- 💾 Intelligent caching for better performance

### Tools & Features
| Command | Description |
|---------|-------------|
| `f`, `filter` | Show/modify search filters |
| `h`, `history` | Display search history |
| `s`, `save` | Save current search |
| `bookmarks` | Show saved bookmarks |

### Interface Commands
| Command | Description |
|---------|-------------|
| `c`, `clear` | Clear screen |
| `r`, `refresh` | Refresh current search |
| `help`, `?` | Show help |
| `exit`, `quit` | Exit application |

## ⚙️ Configuration

### Config File Location
- **Linux/Mac**: `~/.config/searchengine/config.yaml` (or `~/.searchengine/config.yaml` if permission issues)
- **Windows**: `%APPDATA%\searchengine\config.yaml`

### Example Configuration
```yaml
# SearchEngine Pro Configuration
search:
  results_per_page: 10
  default_timeout: 30
  max_retries: 3
  
display:
  colors: true
  animations: true
  unicode_symbols: true
  
filters:
  safe_search: moderate
  default_language: en
  default_region: us
  
history:
  max_entries: 1000
  save_to_file: true
  
api:
  user_agent: "SearchEngine Pro/3.2"
  request_delay: 0.5
```

## 🏗️ Project Structure

```
SearchEnginePro/
├── src/
│   └── searchengine/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── engine.py        # Main search engine
│       │   ├── models.py        # Data models
│       │   ├── filters.py       # Search filtering
│       │   └── history.py       # Search history
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── console.py       # Console interface
│       │   ├── display.py       # Result display
│       │   └── commands.py      # Command processing
│       ├── api/
│       │   ├── __init__.py
│       │   ├── providers.py     # Search providers
│       │   ├── parsers.py       # Result parsers
│       │   └── client.py        # HTTP client
│       └── utils/
│           ├── __init__.py
│           ├── config.py        # Configuration
│           ├── cache.py         # Caching system
│           └── helpers.py       # Utility functions
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── docs/                        # Documentation
├── config/                      # Configuration files
├── examples/                    # Usage examples
├── scripts/                     # Utility scripts
└── data/                        # Data files
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/searchengine

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

## 📚 Documentation

- **[User Guide](docs/user_guide.md)**: Complete usage instructions
- **[API Reference](docs/api_reference.md)**: Developer documentation
- **[Configuration Guide](docs/configuration.md)**: Setup and customization
- **[Contributing](docs/contributing.md)**: Development guidelines

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Add type hints for all functions
- Write comprehensive docstrings

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python and love ❤️
- Inspired by traditional command-line tools
- Thanks to all contributors and users

## 📞 Support

- **Documentation**: [https://searchengine-pro.readthedocs.io/](https://searchengine-pro.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/msadeqsirjani/SearchEnginePro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/msadeqsirjani/SearchEnginePro/discussions)

---

**Made with ❤️ by the SearchEngine Pro Team** 
