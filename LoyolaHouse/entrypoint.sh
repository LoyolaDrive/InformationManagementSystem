#!/bin/bash

# Install netcat if not already installed
apt-get update && apt-get install -y netcat-openbsd

# Wait for database to be ready
echo "Waiting for MySQL database to be ready..."
while ! nc -z db 3306; do
  sleep 0.5
done
echo "MySQL database is ready!"

# Set Django settings module to use Docker settings
export DJANGO_SETTINGS_MODULE=LoyolaHouse.docker_settings

# Create database tables if they don't exist
echo "Creating database tables..."
python manage.py makemigrations

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate sessions
python manage.py migrate admin
python manage.py migrate Users
python manage.py migrate LoyolaSystem

# Create superuser if not exists
echo "Checking for superuser..."
python manage.py shell -c "
try:
    from django.contrib.auth.models import User
    from Users.models import roles, UserRole
    from LoyolaSystem.models import EmailLevel, EmailType
    
    # Create admin superuser if not exists
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'User'
        admin_user.save()
        
        # Create admin role if not exists
        admin_role, created = roles.objects.get_or_create(role_desc='Admin')
        
        # Assign admin role to admin user
        UserRole.objects.create(user=admin_user, role_id=admin_role.role_id)
        print('Superuser created with Admin role.')
    else:
        # Update existing admin user email if needed
        admin_user = User.objects.get(username='admin')
        admin_user.email = 'admin@gmail.com'
        admin_user.set_password('admin')
        admin_user.save()
        print('Existing superuser updated.')

    # Create user roles if they don't exist
    user_roles = ['Admin', 'Regular']
    for role in user_roles:
        roles.objects.get_or_create(role_desc=role)
    
    # Create email levels if they don't exist
    email_levels = ['National', 'Regional', 'Global', 'Local']
    for level in email_levels:
        EmailLevel.objects.get_or_create(level_desc=level)
    print(f'Email levels created: {email_levels}')
    
    # Create email types if they don't exist
    email_types = ['Submission', 'Announcement', 'Reminders']
    for type_desc in email_types:
        EmailType.objects.get_or_create(type_desc=type_desc)
    print(f'Email types created: {email_types}')

except Exception as e:
    print(f'Error in setup: {e}')
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
