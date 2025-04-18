# Loyola House Project

A Django-based system for managing information for Loyola House, including user profiles, announcements, and calendar events.

## Docker Setup

This project is configured to run in Docker containers for easy deployment and development.

### Prerequisites

- Docker
- Docker Compose

### Getting Started

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Loyola-Project/LoyolaHouse
   ```

2. Build and start the containers:
   ```
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. Access the application:
   - Web application: http://localhost:8000
   - Default admin credentials:
     - Username: admin
     - Password: admin

### Docker Components

- **Web Container**: Runs the Django application
- **Database Container**: Runs MySQL 8.0

### Environment Variables

The following environment variables can be modified in the `docker-compose.dev.yml` file:

- `DATABASE_NAME`: MySQL database name (default: LoyolaDB)
- `DATABASE_USER`: MySQL username (default: loyola_user)
- `DATABASE_PASSWORD`: MySQL password (default: loyola_password)
- `DATABASE_HOST`: MySQL host (default: db)
- `DATABASE_PORT`: MySQL port (default: 3306)

## Development

For development purposes, the application code is mounted as a volume, so changes made to the code will be reflected in the running container.

### Making Changes

1. Make changes to the code
2. The Django development server will automatically reload

### Running Migrations

Migrations are automatically applied when the container starts. If you need to run migrations manually:

```
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### Creating a Superuser

A default superuser is created automatically. If you need to create another superuser:

```
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

## Production Deployment

For production deployment, additional configuration is recommended:

1. Set `DEBUG=False` in settings
2. Use a proper web server like Nginx
3. Use Gunicorn or uWSGI instead of the Django development server
4. Set secure and unique passwords for the database
5. Configure proper email settings

## Security Notes

- The default admin credentials should be changed in production
- Sensitive information should be stored in environment variables, not in the code
