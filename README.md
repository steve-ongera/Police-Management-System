# Police Management System

A comprehensive Django-based web application for managing police department operations, including incident reporting, evidence tracking, personnel management, and emergency call dispatch.

## 🚔 Features

### Core Functionality
- **Incident Management**: Complete incident lifecycle from reporting to resolution
- **Personnel Management**: Officer profiles, shifts, and duty assignments
- **Evidence Tracking**: Chain of custody with file attachments
- **Emergency Dispatch**: 911 call management and response tracking
- **Arrest Records**: Comprehensive arrest and booking system
- **Court Case Management**: Legal proceedings and case status tracking
- **Vehicle Management**: Fleet tracking and stolen vehicle alerts
- **Equipment Management**: Asset tracking and maintenance scheduling

### Administrative Features
- **Multi-level User Roles**: Admin, Officer, Detective, Supervisor, Dispatcher
- **Department & Station Management**: Organizational structure
- **Audit Trail**: Complete system activity logging
- **Report Generation**: Automated police reports
- **Dashboard Analytics**: Key performance indicators and statistics

## 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL 13+
- **Authentication**: Django's built-in auth system
- **Admin Interface**: Enhanced Django Admin
- **File Storage**: Django's file handling system
- **API**: Django REST Framework (if needed)

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 13+
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv, or conda)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/police-management-system.git
cd police-management-system
```

### 2. Create Virtual Environment
```bash
# Using venv
python -m venv police_env
source police_env/bin/activate  # On Windows: police_env\Scripts\activate

# Or using conda
conda create -n police_env python=3.9
conda activate police_env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Setup

#### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# Download and install from https://www.postgresql.org/download/
```

#### Create Database and User
```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE police_management_db;
CREATE USER police_user WITH PASSWORD 'your_secure_password';
ALTER ROLE police_user SET client_encoding TO 'utf8';
ALTER ROLE police_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE police_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE police_management_db TO police_user;
\q
```

### 5. Environment Configuration

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=police_management_db
DB_USER=police_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Media and Static Files
MEDIA_URL=/media/
STATIC_URL=/static/
```

### 6. Django Setup

#### Update settings.py
```python
# settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

#### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser
```bash
python manage.py createsuperuser
```

#### Collect Static Files
```bash
python manage.py collectstatic
```

### 7. Load Initial Data (Optional)
```bash
python manage.py loaddata fixtures/initial_data.json
```

## 🏃‍♂️ Running the Application

### Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.
Admin interface: `http://127.0.0.1:8000/admin/`

### Production Deployment

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn police_management.wsgi:application --bind 0.0.0.0:8000
```

#### Using Docker (Optional)
```bash
# Build image
docker build -t police-management .

# Run container
docker run -p 8000:8000 -e DATABASE_URL=postgresql://user:password@host:port/dbname police-management
```

## 📁 Project Structure

```
police-management-system/
├── police_management/          # Main project directory
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                   # Core models and functionality
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── incidents/              # Incident management
│   ├── personnel/              # Staff management
│   ├── evidence/               # Evidence tracking
│   └── dispatch/               # Emergency calls
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User uploads
├── templates/                  # HTML templates
├── fixtures/                   # Initial data
├── requirements.txt
├── manage.py
├── .env.example
└── README.md
```

## 👥 User Roles & Permissions

### Administrator
- Full system access
- User management
- System configuration
- Audit log access

### Supervisor
- Department oversight
- Officer management
- Case assignments
- Report reviews

### Detective
- Case investigations
- Evidence management
- Suspect interviews
- Court case preparation

### Officer
- Incident reporting
- Patrol logs
- Evidence collection
- Arrest processing

### Dispatcher
- Emergency call handling
- Unit dispatching
- Communication logs
- Priority management

## 📊 Database Schema

### Key Tables
- `auth_user` - Extended user model with police-specific fields
- `core_incident` - Main incident records
- `core_person` - Suspects, victims, witnesses
- `core_evidence` - Evidence items with chain of custody
- `core_emergencycall` - 911 calls and dispatch
- `core_arrest` - Arrest records and charges
- `core_courtcase` - Legal proceedings
- `core_auditlog` - System activity tracking

### Relationships
- One-to-many: Incident → Evidence, Reports, Arrests
- Many-to-many: Incident ↔ Person, Incident ↔ Vehicle
- Foreign keys: User → Incidents, Stations → Users

## 🔐 Security Features

- **Authentication**: Django's built-in user authentication
- **Authorization**: Role-based access control
- **Audit Trail**: Complete activity logging
- **Data Encryption**: Sensitive data protection
- **Session Management**: Secure session handling
- **CSRF Protection**: Cross-site request forgery prevention

## 🧪 Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.core

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Data
```bash
python manage.py loaddata fixtures/test_data.json
```

## 📈 Performance Optimization

### Database Optimization
```python
# Use select_related for foreign keys
incidents = Incident.objects.select_related('crime_type', 'reporting_officer')

# Use prefetch_related for many-to-many
incidents = Incident.objects.prefetch_related('evidences', 'persons')

# Database indexing
class Meta:
    indexes = [
        models.Index(fields=['incident_number']),
        models.Index(fields=['date_occurred']),
    ]
```

### Caching (Optional)
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## 🔧 Configuration Options

### Email Settings
Configure SMTP for notifications:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### File Upload Settings
```python
# Maximum file size (10MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Allowed file types
ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.mp4']
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Test connection
psql -h localhost -U police_user -d police_management_db
```

#### Migration Issues
```bash
# Reset migrations (development only)
python manage.py migrate core zero
python manage.py makemigrations core
python manage.py migrate
```

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --clear

# Check STATIC_ROOT in settings.py
```

#### Permission Denied Errors
```bash
# Fix file permissions
chmod -R 755 media/
chown -R www-data:www-data media/
```

## 📝 API Documentation

If using Django REST Framework:
```bash
# Install DRF
pip install djangorestframework

# Access API docs at:
http://127.0.0.1:8000/api/docs/
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Code formatting
black .
isort .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [Wiki](https://github.com/steve-ongera/police-management-system/wiki)
- **Issues**: [GitHub Issues](https://github.com/steve-ongera/police-management-system/issues)
- **Email**: support@steveongera.com

## 🔄 Changelog

### Version 1.0.0 (2024)
- Initial release
- Core incident management
- Evidence tracking system
- User role management
- Admin interface

### Version 1.1.0 (Planned)
- Mobile responsive design
- REST API endpoints
- Real-time notifications
- Advanced reporting features

## 🙏 Acknowledgments

- Django Framework contributors
- PostgreSQL development team
- Open source community
- Law enforcement professionals who provided requirements

---

**⚠️ Important Security Notice**: This system handles sensitive law enforcement data. Ensure proper security measures, access controls, and compliance with local regulations before deployment in production environments.