# Dream AI Test Commands Quick Reference

## Installation & Setup

```bash
# Install Python test dependencies
pip install -r requirements-test.txt

# Install Playwright browsers (for E2E tests)
playwright install chromium

# Make test runner script executable (Unix/Mac)
chmod +x run-tests.sh
```

## Running Tests

### Quick Commands

```bash
# Run all tests
npm test

# Run only unit tests (fastest)
npm run test:unit

# Run only integration tests
npm run test:integration

# Run only E2E tests (requires running app)
npm run test:e2e

# Run tests and stop on first failure
npm run test:fast
```

### Using Pytest Directly

```bash
# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_financial_calcs.py -v

# Run specific test class
pytest tests/unit/test_financial_calcs.py::TestIRRCalculation -v

# Run specific test
pytest tests/unit/test_financial_calcs.py::TestIRRCalculation::test_simple_irr -v

# Run tests by category
pytest tests/unit/ -v          # Unit tests only
pytest tests/integration/ -v   # Integration tests only
pytest tests/e2e/ -v           # E2E tests only
```

### Using Test Markers

```bash
# Run only financial calculation tests
pytest -m financial -v

# Run only scenario tests
pytest -m scenario -v

# Skip slow tests
pytest -m "not slow" -v

# Run only unit tests
pytest -m unit -v

# Run integration tests
pytest -m integration -v
```

## Coverage Reports

```bash
# Generate HTML coverage report
npm run test:coverage

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Generate XML coverage (for CI)
npm run test:ci

# Show coverage in terminal
pytest tests/unit/ tests/integration/ --cov=src --cov-report=term-missing
```

## E2E Test Options

```bash
# Run E2E tests in headed mode (see browser)
pytest tests/e2e/ --headed

# Run E2E tests with slow motion (for debugging)
pytest tests/e2e/ --headed --slowmo=500

# Take screenshots on failure
pytest tests/e2e/ --screenshot=on

# Record video of tests
pytest tests/e2e/ --video=on

# Debug specific test
PWDEBUG=1 pytest tests/e2e/test_critical_paths.py::test_create_new_deal
```

## Advanced Options

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Stop on first failure
pytest -x

# Run last failed tests only
pytest --lf

# Run tests matching pattern
pytest -k "test_irr"

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Disable warnings
pytest --disable-warnings
```

## Performance & Benchmarking

```bash
# Time each test
pytest --durations=10

# Profile tests
pytest --profile

# Benchmark tests (requires pytest-benchmark)
pytest tests/unit/ --benchmark-only
```

## Test Reports

```bash
# Generate HTML test report
pytest --html=report.html --self-contained-html

# Generate JSON test report
pytest --json-report --json-report-file=report.json

# Generate JUnit XML (for CI)
pytest --junit-xml=junit.xml
```

## Continuous Testing

```bash
# Watch mode - rerun on file changes (requires pytest-watch)
pytest-watch tests/

# Rerun only failed tests on changes
pytest --looponfail tests/
```

## Pre-Commit Checks

```bash
# Quick pre-commit test (unit + integration only)
npm run test:fast

# Full test suite before PR
npm test

# Check code formatting
black tests/ --check

# Lint tests
flake8 tests/ --max-line-length=120

# Type check tests
mypy tests/ --ignore-missing-imports
```

## CI/CD Commands

```bash
# Run tests as CI would
npm run test:ci

# Simulate CI environment
CI=true pytest tests/ -v --cov=src --cov-report=xml

# Check GitHub Actions workflow locally (requires act)
act -j unit-and-integration-tests
```

## Troubleshooting

```bash
# Clear pytest cache
pytest --cache-clear

# Show available fixtures
pytest --fixtures

# Show available markers
pytest --markers

# Collect tests without running
pytest --collect-only

# Verbose output with locals
pytest -vv --showlocals

# Full traceback
pytest --tb=long
```

## Environment Variables

```bash
# Run in headed mode (E2E tests)
HEADED=1 pytest tests/e2e/

# Set custom base URL for E2E tests
BASE_URL=http://localhost:3000 pytest tests/e2e/

# Enable debug mode for Playwright
PWDEBUG=1 pytest tests/e2e/

# Set timeout for tests
PYTEST_TIMEOUT=60 pytest tests/
```

## Fixture Usage

```bash
# List available fixtures
pytest --fixtures tests/

# Use specific fixture in test
pytest tests/ --fixtures-per-test

# Show fixture setup/teardown
pytest -v --setup-show
```

## Common Workflows

### Development Workflow
```bash
# 1. Make changes to code
# 2. Run fast tests
npm run test:fast

# 3. If tests pass, commit
git add .
git commit -m "feature: description"

# 4. Before push, run full suite
npm test

# 5. Push
git push
```

### Debugging Failed Test
```bash
# 1. Run specific failing test with verbose output
pytest tests/unit/test_financial_calcs.py::test_simple_irr -vv

# 2. Run with debugger
pytest tests/unit/test_financial_calcs.py::test_simple_irr --pdb

# 3. Show print statements
pytest tests/unit/test_financial_calcs.py::test_simple_irr -s
```

### Adding New Test
```bash
# 1. Write test in appropriate file
# 2. Run new test to ensure it works
pytest tests/unit/test_financial_calcs.py::test_my_new_test -v

# 3. Run all tests in file
pytest tests/unit/test_financial_calcs.py -v

# 4. Check coverage
pytest tests/unit/ --cov=src --cov-report=term-missing
```

## Performance Targets

```bash
# Unit tests should be <1ms each
pytest tests/unit/ --durations=0

# Integration tests should be <10ms each
pytest tests/integration/ --durations=0

# E2E tests should be <30s each
pytest tests/e2e/ --durations=0

# Total suite should complete in <5 minutes
time npm test
```

## Test Data

```bash
# View test fixtures
cat tests/fixtures/mock_deals.json

# Add new fixture
echo '{"new_deal": {...}}' >> tests/fixtures/mock_deals.json

# Validate fixture format
python -m json.tool tests/fixtures/mock_deals.json
```

---

## Quick Reference Card

| Command | Description |
|---------|-------------|
| `npm test` | Run all tests |
| `npm run test:unit` | Unit tests only |
| `npm run test:integration` | Integration tests only |
| `npm run test:e2e` | E2E tests only |
| `npm run test:fast` | Unit + Integration (fast) |
| `npm run test:coverage` | Generate coverage report |
| `pytest -m financial` | Run financial tests only |
| `pytest -m scenario` | Run scenario tests only |
| `pytest -x` | Stop on first failure |
| `pytest --lf` | Run last failed |
| `pytest -k "test_irr"` | Run tests matching pattern |
| `pytest --headed` | E2E with visible browser |
| `pytest --pdb` | Debug on failure |

---

**See Also:**
- Full documentation: `tests/README.md`
- Test architecture: `TEST_ARCHITECTURE.md`
- Implementation summary: `TEST_QA_SUMMARY.md`

