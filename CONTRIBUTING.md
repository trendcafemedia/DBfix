# Contributing to DBfix

Thank you for your interest in contributing to DBfix! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

There are many ways to contribute to DBfix:

1. **Reporting Bugs**: If you find a bug, please create an issue with a detailed description of the problem, steps to reproduce, and your environment.

2. **Suggesting Enhancements**: Have an idea for a new feature or improvement? Create an issue with the "enhancement" label.

3. **Code Contributions**: Want to fix a bug or implement a feature? Follow the steps below.

4. **Documentation**: Help improve the documentation by fixing errors or adding missing information.

5. **Testing**: Help test the application and report any issues you find.

## Development Workflow

### Setting Up the Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/DBfix.git
   cd DBfix
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Making Changes

1. Make your changes to the codebase
2. Add tests for your changes
3. Run the tests to ensure they pass:
   ```bash
   pytest
   ```
4. Update documentation if necessary
5. Commit your changes with a descriptive commit message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

### Submitting a Pull Request

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Go to the original repository on GitHub and create a pull request
3. Describe your changes in detail
4. Wait for a maintainer to review your pull request
5. Address any feedback or requested changes

## Coding Standards

### Python Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules
- Keep functions focused on a single responsibility
- Use type hints where appropriate

### Testing

- Write tests for all new features and bug fixes
- Aim for high test coverage
- Tests should be independent of each other
- Mock external dependencies when appropriate

### Documentation

- Update documentation for any changes to the API or functionality
- Use clear, concise language
- Include code examples where appropriate
- Keep documentation up-to-date with code changes

## Project Structure

- `core/`: Core repair engine
- `legacy/`: Original scripts for reference
- `docs/`: Documentation
- `gui/`: GUI application (planned)
- `web/`: Web application (planned)
- `tests/`: Test suite

## Getting Help

If you need help with contributing, please:

1. Check the documentation
2. Look for similar issues on GitHub
3. Create a new issue with the "question" label

## License

By contributing to DBfix, you agree that your contributions will be licensed under the project's MIT License.
