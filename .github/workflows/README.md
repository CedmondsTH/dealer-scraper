# GitHub Actions Workflows

This directory contains CI/CD workflows for the dealer scraper project.

## Workflows

### CI Pipeline (`ci.yml`)

Runs on every push and pull request to validate code quality.

**Jobs:**
- **test**: Runs unit tests on Python 3.10 and 3.11
- **lint**: Checks code formatting (Black, isort, Flake8) and type hints (mypy)
- **security**: Scans for security vulnerabilities (Safety, Bandit)

### Integration Tests (`integration-tests.yml`)

Runs comprehensive integration tests with real network requests.

**Triggers:**
- Daily at 2 AM UTC (scheduled)
- Manual trigger via workflow_dispatch
- Push to main branch (paths: scrapers, services, integration tests)

**Timeout:** 30 minutes

## Status Badges

Add these badges to your README.md:

```markdown
![CI Pipeline](https://github.com/CedmondsTH/dealer-scraper/workflows/CI%20Pipeline/badge.svg)
![Integration Tests](https://github.com/CedmondsTH/dealer-scraper/workflows/Integration%20Tests/badge.svg)
[![codecov](https://codecov.io/gh/CedmondsTH/dealer-scraper/branch/main/graph/badge.svg)](https://codecov.io/gh/CedmondsTH/dealer-scraper)
```

## Local Development

Before pushing code, run these checks locally:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Run linters
flake8 src/ tests/ --max-line-length=120
mypy src/

# Run tests
pytest tests/ -m "not slow"
```

## Troubleshooting

### Test Failures

Check the test artifacts uploaded to GitHub Actions for detailed reports.

### Security Alerts

Review the Bandit security report artifact for any security issues detected.

### Slow Tests

Integration tests are marked with `@pytest.mark.slow` and run separately to keep the CI pipeline fast.

