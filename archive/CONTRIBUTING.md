# Contributing to Dealer Scraper

Thank you for your interest in contributing to the Dealer Scraper project! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. Check existing issues first
2. Use the issue template
3. Provide detailed reproduction steps
4. Include environment information

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Ensure all tests pass: `make test`
6. Run quality checks: `make quality`
7. Commit with descriptive messages
8. Push to your fork
9. Submit a pull request

## 🏗️ Development Setup

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd dealer-scraper

# Set up development environment
make setup

# Or manually:
make install-dev
```

### Development Commands

```bash
# Run tests
make test

# Check code quality
make quality

# Format code
make format

# Run the application
make run

# Full development check
make dev-check
```

## 📋 Coding Standards

### Python Style

- **PEP 8** compliance via `flake8`
- **Black** for code formatting
- **isort** for import sorting
- **Type hints** required for all functions
- **Docstrings** required for all public functions

### Architecture Principles

- **Single Responsibility**: Each class/function has one clear purpose
- **Open/Closed**: Easy to extend, hard to modify existing code
- **Dependency Injection**: Services should be injectable for testing
- **Strategy Pattern**: New dealer sites should be separate strategies

### File Organization

```
dealer-scraper/
├── core/           # Business logic services
├── scrapers/       # Scraping strategies
├── utils/          # Shared utilities
├── config/         # Configuration management
├── cli/            # Command-line interface
├── ui/             # Web interface
├── tests/          # Test files
├── docs/           # Documentation
├── scripts/        # Development scripts
└── assets/         # Static files (images, etc.)
```

## 🧪 Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test full workflows

### Writing Tests

```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = "test input"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Test Requirements

- All new features must have tests
- Aim for >80% code coverage
- Tests should be fast and isolated
- Use descriptive test names

## 🎯 Adding New Dealer Sites

### 1. Create Strategy Class

```python
# scrapers/strategies/new_dealer_strategy.py
from ..base_scraper import ScraperStrategy

class NewDealerStrategy(ScraperStrategy):
    @property
    def strategy_name(self) -> str:
        return "New Dealer Site"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        # Detection logic
        return "new-dealer-indicator" in html
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict]:
        # Extraction logic
        pass
```

### 2. Register Strategy

```python
# scrapers/strategy_manager.py
from .strategies.new_dealer_strategy import NewDealerStrategy

def initialize_strategies():
    # Add to registration
    scraper_registry.register(NewDealerStrategy())
```

### 3. Add Tests

```python
# tests/test_new_dealer_strategy.py
def test_new_dealer_detection():
    """Test that strategy correctly detects new dealer sites."""
    pass

def test_new_dealer_extraction():
    """Test data extraction from new dealer sites."""
    pass
```

## 📝 Documentation Standards

### Code Documentation

- **Docstrings**: All public functions, classes, and modules
- **Type hints**: All function parameters and return values
- **Comments**: Complex logic should be explained

### README Updates

- Update feature lists when adding new functionality
- Include usage examples for new features
- Update architecture diagrams if needed

## 🔒 Security Guidelines

### Data Handling

- Never log sensitive data (URLs with tokens, personal information)
- Validate all inputs from external sources
- Use secure browser settings for scraping

### Dependencies

- Keep dependencies up to date
- Run security checks: `make security`
- Review dependency licenses

## 🚀 Release Process

### Version Numbering

We use semantic versioning (SemVer):
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

### Release Checklist

1. Update version in `pyproject.toml`
2. Run full test suite: `make ci`
3. Update CHANGELOG.md
4. Create release branch
5. Submit pull request
6. Tag release after merge

## 🐛 Debugging Guidelines

### Common Issues

1. **Playwright failures**: Check browser installation
2. **Import errors**: Verify Python path and dependencies
3. **Strategy not triggering**: Check `can_handle()` logic

### Debug Tools

```bash
# Enable debug mode
python main.py scrape "Dealer" "URL" --debug

# Check available strategies
python main.py list-strategies

# Run with verbose logging
LOG_LEVEL=DEBUG python main.py
```

## 📞 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Code Review**: All PRs receive thorough review

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributor section
- Release notes
- Git commit history

Thank you for helping make Dealer Scraper better! 🎉