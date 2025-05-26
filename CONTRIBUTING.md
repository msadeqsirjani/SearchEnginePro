# Contributing to SearchEngine Pro

First off, thank you for considering contributing to SearchEngine Pro! It's people like you that make SearchEngine Pro such a great tool.

## 🚀 Quick Start

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/msadeqsirjani/SearchEnginePro.git
   cd SearchEnginePro
   ```

2. **Set up your development environment**
   ```bash
   # Create a virtual environment
   python -m venv .venv
   
   # Activate it
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

3. **Install development tools**
   ```bash
   pip install black isort flake8 mypy pytest pytest-cov pre-commit
   
   # Set up pre-commit hooks
   pre-commit install
   ```

## 🛠️ Development Guidelines

### Code Style

We use several tools to maintain consistent code quality:

- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking

Run these before committing:
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Testing

We maintain high test coverage. Please add tests for any new functionality:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/searchengine --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(search): add advanced query parsing
fix(ui): resolve pagination display issue
docs(readme): update installation instructions
```

## 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

**Use our bug report template** with the following information:

- **Environment details** (OS, Python version, etc.)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Error messages** (full stack trace if available)
- **Screenshots** if applicable

## 💡 Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing feature requests** to avoid duplicates
2. **Describe the problem** you're trying to solve
3. **Explain the proposed solution** in detail
4. **Consider backwards compatibility**
5. **Provide examples** of how the feature would be used

## 📋 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   # Run the full test suite
   pytest
   
   # Check code quality
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Use our PR template
   - Reference any related issues
   - Describe what you changed and why
   - Include screenshots for UI changes

### Pull Request Requirements

- [ ] Code follows our style guidelines
- [ ] All tests pass
- [ ] New functionality includes tests
- [ ] Documentation is updated
- [ ] Commit messages follow our convention
- [ ] No merge conflicts

## 🏗️ Project Structure

```
SearchEnginePro/
├── src/searchengine/          # Main source code
│   ├── core/                  # Core search engine logic
│   ├── ui/                    # User interface components
│   ├── api/                   # API providers and clients
│   └── utils/                 # Utility functions
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                      # Documentation
├── config/                    # Configuration files
└── examples/                  # Usage examples
```

## 🔧 Development Tips

### Setting up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# Run against all files (optional)
pre-commit run --all-files
```

### Running Tests in Different Environments

```bash
# Test against multiple Python versions using tox
pip install tox
tox

# Test specific Python version
tox -e py39
```

### Debugging

- Use `pytest -s` to see print statements
- Use `pytest --pdb` to drop into debugger on failures
- Add `breakpoint()` in your code for debugging

## 📚 Documentation

### Updating Documentation

- API documentation uses docstrings (Google style)
- User guides are in Markdown
- Code examples should be runnable

### Building Documentation Locally

```bash
# Install docs dependencies
pip install -r docs/requirements.txt

# Build documentation
cd docs/
make html

# View in browser
open _build/html/index.html
```

## 🤝 Community Guidelines

### Code of Conduct

This project adheres to a Code of Conduct that we expect all contributors to follow:

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Be patient** with newcomers
- **Focus on what's best** for the community

### Getting Help

- **Documentation**: Check our comprehensive docs
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community chat (link in README)

## 🎯 Good First Issues

Looking for a way to contribute? Check out issues labeled:
- `good first issue` - Perfect for newcomers
- `help wanted` - We'd love community help
- `documentation` - Help improve our docs
- `bug` - Fix reported issues

## 🏆 Recognition

Contributors are recognized in several ways:
- Listed in our CONTRIBUTORS.md file
- Mentioned in release notes for significant contributions
- Given commit access for sustained contributors
- Invited to join our core team

## 📞 Contact

- **Maintainer**: [@msadeqsirjani](https://github.com/msadeqsirjani)
- **Issues**: [GitHub Issues](https://github.com/msadeqsirjani/SearchEnginePro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/msadeqsirjani/SearchEnginePro/discussions)

---

Thank you for contributing to SearchEngine Pro! 🚀 