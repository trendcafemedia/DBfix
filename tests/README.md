# DBfix Tests

This directory contains tests for the DBfix SQLite Database Repair Tool.

## Test Structure

- `test_repair_engine.py`: Tests for the core repair engine
- Additional test files will be added as new features are implemented

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=core

# Run specific test file
pytest tests/test_repair_engine.py

# Run specific test
pytest tests/test_repair_engine.py::TestDatabaseRepairTool::test_repair_database
```

## Test Data

The tests create temporary test databases and corrupted versions for testing the repair functionality. No external test data is required.

## Adding New Tests

When adding new features, please add corresponding tests following these guidelines:

1. Create a new test file if testing a new module
2. Use descriptive test names that explain what is being tested
3. Include both positive and negative test cases
4. Mock external dependencies when appropriate
5. Keep tests independent of each other

## Test Coverage Goals

- Core repair engine: 90%+
- GUI components: 80%+
- Web components: 80%+
