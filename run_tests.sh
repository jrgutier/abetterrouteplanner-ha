#!/bin/bash
# Test runner script for ABRP integration

set -e

echo "================================"
echo "ABRP Integration Test Runner"
echo "================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and add your credentials to run integration tests"
    echo ""
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -q -r requirements-test.txt
echo "✅ Dependencies installed"
echo ""

# Run different test suites based on argument
case "${1:-all}" in
    unit)
        echo "🧪 Running unit tests only..."
        pytest -v -m unit tests/
        ;;
    integration)
        echo "🧪 Running integration tests only..."
        if [ ! -f .env ]; then
            echo "❌ Error: .env file required for integration tests"
            exit 1
        fi
        pytest -v -m integration tests/
        ;;
    coverage)
        echo "🧪 Running all tests with coverage..."
        pytest -v --cov=custom_components.abetterrouteplanner --cov-report=html --cov-report=term tests/
        echo ""
        echo "📊 Coverage report generated in htmlcov/index.html"
        ;;
    *)
        echo "🧪 Running all unit tests..."
        pytest -v -m unit tests/
        echo ""
        echo "💡 To run integration tests: ./run_tests.sh integration"
        echo "💡 To run with coverage: ./run_tests.sh coverage"
        ;;
esac

echo ""
echo "✅ Tests completed!"
