# DBfix Web Application

This directory contains the web application version of the DBfix SQLite Database Repair Tool. The web application provides a SaaS (Software as a Service) implementation with subscription-based pricing and WordPress integration capabilities.

## Status

🚧 **Under Development** 🚧

The web application is currently in the planning and development phase. See the [roadmap](../docs/business/roadmap.md) for more details on the development timeline.

## Directory Structure

- `api/`: Backend API implementation
- `frontend/`: Frontend web application
- `wordpress/`: WordPress integration components

## Planned Features

- **Modern Web Interface**: Responsive design for all devices
- **User Authentication**: Secure account management
- **Subscription Tiers**: Free, Basic, Professional, and Enterprise plans
- **Database Upload/Download**: Secure file handling
- **Asynchronous Processing**: Background processing for large databases
- **Interactive Reports**: Detailed visual reports of the repair process
- **WordPress Integration**: Connect with existing WordPress sites
- **API Access**: Programmatic access for Enterprise subscribers

## Technology Stack

### Backend
- **Flask/FastAPI**: Python web framework
- **PostgreSQL**: User and subscription data storage
- **Redis**: Job queue and caching
- **Celery**: Asynchronous task processing
- **Core Repair Engine**: Integration with the existing repair engine

### Frontend
- **React/Vue.js**: Frontend framework
- **Tailwind CSS**: Styling
- **Chart.js/D3.js**: Data visualization
- **Axios**: API communication

### WordPress Integration
- **Custom Plugin**: Authentication and embedding
- **REST API**: Communication between WordPress and the web app

## WordPress Integration

The web application includes a WordPress connector plugin that allows:

- **Single Sign-On**: WordPress users can access the repair tool without re-authentication
- **Embedded Components**: Repair tool components can be embedded in WordPress pages
- **Consistent Branding**: Maintain visual consistency with your WordPress site
- **User Management**: Leverage existing WordPress user database

See [wordpress_integration_strategy.md](../docs/business/wordpress_integration_strategy.md) for detailed information.

## Development Setup (Future)

```bash
# Backend setup
cd api
pip install -r requirements.txt
python run.py

# Frontend setup
cd frontend
npm install
npm run dev

# WordPress plugin setup
cd wordpress
composer install
```

## API Documentation (Future)

API documentation will be available at `/api/docs` when the server is running.

## Contributing

Contributions to the web application development are welcome! Please see the main [CONTRIBUTING.md](../CONTRIBUTING.md) file for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
