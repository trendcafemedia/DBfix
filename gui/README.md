# DBfix GUI Application

This directory contains the graphical user interface (GUI) for the DBfix SQLite Database Repair Tool. The GUI provides a user-friendly way to interact with the repair engine, making it accessible to non-technical users.

## Status

🚧 **Under Development** 🚧

The GUI application is currently in the planning and development phase. See the [roadmap](../docs/business/roadmap.md) for more details on the development timeline.

## Planned Features

- **Intuitive Interface**: Simple, user-friendly design for all skill levels
- **Database Preview**: View database structure and contents before repair
- **Repair Strategy Selection**: Choose from multiple repair strategies or use automatic selection
- **Progress Tracking**: Real-time progress indicators for repair operations
- **Visual Reports**: Interactive visual reports of the repair process
- **Batch Processing**: Repair multiple databases in one operation
- **Dark/Light Themes**: Support for different visual preferences
- **Cross-platform**: Windows, macOS, and Linux support

## Technology Stack

The GUI application will be built using:

- **PySide6** (Qt for Python): Modern, cross-platform GUI framework
- **SQLite Viewer Components**: For database structure visualization
- **Matplotlib/Plotly**: For data visualization in reports
- **Core Repair Engine**: Integration with the existing repair engine

## Development Approach

1. **Phase 1**: Basic interface with file selection and repair options
2. **Phase 2**: Database preview and visualization features
3. **Phase 3**: Advanced features (batch processing, settings, etc.)

## Getting Started (Future)

```bash
# Install dependencies
pip install -r gui/requirements.txt

# Run the GUI application
python -m gui.main
```

## Screenshots

(Screenshots will be added as development progresses)

## Contributing

Contributions to the GUI development are welcome! Please see the main [CONTRIBUTING.md](../CONTRIBUTING.md) file for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
