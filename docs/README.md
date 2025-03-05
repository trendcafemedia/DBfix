# DBfix Documentation

This directory contains documentation for the DBfix SQLite Database Repair Tool.

## Documentation Structure

The documentation is organized into two main sections:

### Technical Documentation

The `technical/` directory contains technical documentation for developers and users:

- Architecture overview
- API reference
- Usage guides
- Development guidelines
- Original documentation from the iMessage_Repair_Tools project

See [technical/README.md](technical/README.md) for more details.

### Business Documentation

The `business/` directory contains business development and commercialization plans:

- Business strategy overview
- Development roadmap
- GUI application plan
- SaaS web application plan
- WordPress integration strategy
- Implementation assessments

See [business/README.md](business/README.md) for more details.

## Contributing to Documentation

When contributing to the documentation:

1. Follow the established structure
2. Use Markdown for all documentation files
3. Include code examples where appropriate
4. Keep documentation up-to-date with code changes
5. Use clear, concise language

## Building Documentation

The project uses Sphinx for generating HTML documentation:

```bash
# Install Sphinx and theme
pip install sphinx sphinx-rtd-theme

# Generate HTML documentation
cd docs
sphinx-build -b html source build/html
```

## Future Documentation Plans

- User tutorials and guides
- API reference documentation
- Troubleshooting guides
- FAQ section
- Video tutorials
