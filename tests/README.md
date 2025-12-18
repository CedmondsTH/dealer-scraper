# Dealer Scraper Test Suite

This directory contains comprehensive tests for the dealer scraper application.

## Test Structure

```
tests/
├── test_address_parser.py      # Unit tests for address parsing
├── test_data_cleaner.py        # Unit tests for data cleaning
├── test_extractors.py          # Unit tests for dealer extractors
└── test_integration_scraping.py # Integration tests for full pipeline
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Only Unit Tests

```bash
pytest -m unit
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see the coverage report.

### Skip Slow Tests

Some integration tests make real network requests and can be slow:

```bash
pytest -m "not slow"
```

## Test Markers

- `unit`: Fast unit tests that don't require external dependencies
- `integration`: Integration tests that verify end-to-end functionality
- `slow`: Tests that make real network requests (may take minutes)

## Writing New Tests

### Unit Tests

Unit tests should be fast and test individual functions/classes in isolation:

```python
def test_clean_name():
    cleaner = DataCleaner()
    result = cleaner.clean_dealership_name("  Toyota  ")
    assert result == "Toyota"
```

### Integration Tests

Integration tests verify the full pipeline works correctly:

```python
@pytest.mark.integration
@pytest.mark.slow
def test_scrape_dealer(scraper_service):
    result = scraper_service.scrape_dealer_locations(
        "Test Dealer",
        "https://example.com/locations"
    )
    assert result.success is True
```

## Coverage Goals

- **Utilities**: > 90% coverage
- **Services**: > 80% coverage
- **Strategies**: > 70% coverage
- **Overall**: > 75% coverage

