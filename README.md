# DBfix: Advanced SQLite Database Repair Tool

DBfix is a comprehensive tool for repairing corrupted SQLite databases with support for multiple repair strategies, detailed reporting, and an intuitive interface.

![DBfix Logo](docs/images/dbfix-logo.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/DBfix.svg)](https://github.com/YOUR_USERNAME/DBfix/issues)

## Features

- **Multiple Repair Strategies**: Intelligent selection of the best repair approach for each database
- **Comprehensive Reporting**: Detailed HTML and JSON reports of the repair process
- **Command-line Interface**: Powerful CLI with multiple options for customization
- **Universal Support**: Works with any SQLite database, not just iMessage
- **Data Recovery**: Partial data extraction for severely corrupted files
- **Cross-platform**: Works on Windows, macOS, and Linux

## Coming Soon

- **GUI Application**: User-friendly interface for non-technical users
- **Web Application**: SaaS version with subscription-based pricing
- **WordPress Integration**: Connect with your existing WordPress site

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/DBfix.git

# Navigate to the project directory
cd DBfix

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
python -m core.repair_engine path/to/database.db [options]
```

Options:
- `-o, --output-dir DIR`: Directory to save repaired database and reports
- `-l, --log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--imessage`: Specify if the database is an iMessage database

### Example

```bash
# Repair a general SQLite database
python -m core.repair_engine my_database.db --output-dir ./repaired

# Repair an iMessage database with debug logging
python -m core.repair_engine chat.db --imessage --log-level DEBUG
```

## Project Structure

- `core/`: Core repair engine
- `legacy/`: Original repair scripts for reference
- `docs/`: Documentation (technical and business)
- `gui/`: GUI application (planned)
- `web/`: Web application and WordPress integration (planned)
- `tests/`: Test suite

## Documentation

- [Technical Documentation](docs/technical/)
- [Business Development](docs/business/)
- [Development Roadmap](docs/business/roadmap.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original iMessage repair scripts that inspired this project
- SQLite team for their amazing database engine
- All contributors and users of DBfix
