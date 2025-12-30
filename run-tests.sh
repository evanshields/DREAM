#!/bin/bash
# Dream AI Test Suite Quick Start
# ================================
# This script sets up and runs the complete test suite

set -e  # Exit on error

echo "🧪 Dream AI Test Suite Setup & Execution"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

# Install Python dependencies
print_info "Installing Python test dependencies..."
if [ -f "requirements-test.txt" ]; then
    pip install -q -r requirements-test.txt
    print_success "Python dependencies installed"
else
    print_error "requirements-test.txt not found"
    exit 1
fi

# Install Playwright browsers (for E2E tests)
print_info "Installing Playwright browsers..."
playwright install chromium --with-deps
print_success "Playwright browsers installed"

# Run unit tests
echo ""
echo "==================================="
echo "Running Unit Tests"
echo "==================================="
pytest tests/unit/ -v --cov=src --cov-report=term-missing

if [ $? -eq 0 ]; then
    print_success "Unit tests passed"
else
    print_error "Unit tests failed"
    exit 1
fi

# Run integration tests
echo ""
echo "==================================="
echo "Running Integration Tests"
echo "==================================="
pytest tests/integration/ -v

if [ $? -eq 0 ]; then
    print_success "Integration tests passed"
else
    print_error "Integration tests failed"
    exit 1
fi

# Prompt to run E2E tests
echo ""
read -p "Run E2E tests? (requires app to be running) [y/N]: " run_e2e

if [[ $run_e2e =~ ^[Yy]$ ]]; then
    # Check if app is running
    print_info "Checking if app is running on http://localhost:5173..."
    
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_success "App is running"
        
        echo ""
        echo "==================================="
        echo "Running E2E Tests"
        echo "==================================="
        pytest tests/e2e/ -v
        
        if [ $? -eq 0 ]; then
            print_success "E2E tests passed"
        else
            print_error "E2E tests failed"
            exit 1
        fi
    else
        print_error "App is not running. Please start the app with 'npm run dev' in another terminal."
        echo "Then run: pytest tests/e2e/"
        exit 1
    fi
else
    print_info "Skipping E2E tests"
    echo "To run E2E tests manually:"
    echo "  1. Start app: npm run dev"
    echo "  2. Run tests: pytest tests/e2e/"
fi

# Generate coverage report
echo ""
echo "==================================="
echo "Generating Coverage Report"
echo "==================================="
pytest tests/unit/ tests/integration/ --cov=src --cov-report=html --quiet

if [ -d "htmlcov" ]; then
    print_success "Coverage report generated: htmlcov/index.html"
    echo ""
    echo "Open coverage report with:"
    echo "  open htmlcov/index.html  # macOS"
    echo "  xdg-open htmlcov/index.html  # Linux"
fi

# Final summary
echo ""
echo "========================================"
echo "✅ Test Suite Complete"
echo "========================================"
echo ""
echo "Summary:"
echo "  ✓ Unit tests: PASSED"
echo "  ✓ Integration tests: PASSED"
if [[ $run_e2e =~ ^[Yy]$ ]]; then
    echo "  ✓ E2E tests: PASSED"
else
    echo "  - E2E tests: SKIPPED"
fi
echo ""
echo "Next steps:"
echo "  • View coverage: htmlcov/index.html"
echo "  • Run specific tests: pytest tests/unit/test_financial_calcs.py"
echo "  • Run with markers: pytest -m financial"
echo ""

