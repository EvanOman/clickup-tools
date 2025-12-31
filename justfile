# Justfile for ClickUp Tools development

# Default recipe - show available commands
default:
    @just --list

# Run linting and tests
check:
    @echo "Running linting..."
    uv run ruff check
    @echo "Running format check..."
    uv run ruff format --check
    @echo "Running tests..."
    uv run pytest --cov=clickup --cov-report=xml --cov-report=term-missing

# Fix linting and formatting issues
fix:
    @echo "Fixing linting issues..."
    uv run ruff check --fix
    @echo "Formatting code..."
    uv run ruff format

# Run tests only
test:
    uv run pytest --cov=clickup --cov-report=xml --cov-report=term-missing

# Fix and then check
fc: fix check

# Install dependencies
install:
    uv sync --dev

# Run specific test file
test-file FILE:
    uv run pytest {{FILE}} -v

# Run tests with specific pattern
test-pattern PATTERN:
    uv run pytest -k "{{PATTERN}}" -v

# Clean up generated files
clean:
    rm -rf .pytest_cache
    rm -rf .coverage
    rm -rf coverage.xml
    rm -rf htmlcov
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Build the package
build:
    uv build

# Run the CLI locally
cli *ARGS:
    uv run clickup {{ARGS}}

# Type checking (currently commented out in CI)
typecheck:
    uv run mypy clickup/

# Full development setup
setup: install
    @echo "Development environment ready!"
    @echo "Run 'just check' to validate your setup"