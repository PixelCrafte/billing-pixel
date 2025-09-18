# Billing Pixel - Professional Invoice & Quote Management System

A comprehensive Django-based billing and invoicing application designed for small to medium businesses. Features multi-tenant architecture, PDF generation, role-based permissions, and modern UI with company branding support.

## 🌟 Features

### Core Functionality
- **Multi-tenant Architecture**: Complete company isolation with role-based access control
- **Invoice Management**: Create, edit, and track invoices with automated numbering
- **Quote/Quotation System**: Generate professional quotes with conversion to invoices
- **Receipt Management**: Track payments with receipt generation
- **Client Management**: Comprehensive customer database with contact information

### Advanced Features
- **PDF Generation**: Branded PDF documents with company colors and logos
- **Role-Based Permissions**: Owner, Admin, Accountant, and User roles
- **Audit Logging**: Complete activity tracking for compliance
- **Responsive Design**: Mobile-friendly interface built with Tailwind CSS
- **API Endpoints**: RESTful APIs for frontend integration
- **Background Tasks**: Celery integration for PDF processing and cleanup

### Business Features
- **Company Branding**: Custom logos, colors, and document prefixes
- **Tax Calculations**: Configurable tax rates and discount handling
- **Payment Tracking**: Multiple payment methods and reference tracking
- **Document Versioning**: Immutable document storage for audit trails
- **Secure PDF Downloads**: Token-based secure document access

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+ (optional, SQLite included for development)
- Redis (optional, for Celery tasks)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd billing-pixel
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   cd theme/static_src
   npm install
   npm run build
   cd ../..
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Seed sample data (optional)**
   ```bash
   python manage.py seed_data
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

### Sample Login Credentials (after seeding)
- **Company 1**: owner1@company1.com / password123
- **Company 2**: owner2@company2.com / password123
- **Company 3**: owner3@company3.com / password123

## 🐳 Docker Deployment

### Quick Start with Docker Compose

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd billing-pixel
   cp .env.example .env
   # Edit .env with production settings
   ```

2. **Build and start services**
   ```bash
   docker-compose up -d
   ```

3. **Run initial setup**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   docker-compose exec web python manage.py seed_data
   ```

The application will be available at `http://localhost` (port 80).

### Services Included
- **Web**: Django application server
- **Database**: PostgreSQL with persistent storage
- **Cache**: Redis for caching and Celery
- **Worker**: Celery worker for background tasks
- **Scheduler**: Celery beat for scheduled tasks
- **Proxy**: Nginx reverse proxy with SSL support

## 📁 Project Structure

```
billing-pixel/
├── billingapp/                 # Main Django application
│   ├── management/            # Management commands
│   │   └── commands/          # Custom management commands
│   ├── migrations/            # Database migrations
│   ├── static/               # Static files
│   ├── templates/            # HTML templates
│   │   └── billingapp/       # App-specific templates
│   │       └── pdf/          # PDF templates
│   ├── models.py             # Database models
│   ├── views.py              # View controllers
│   ├── forms.py              # Django forms
│   ├── urls.py               # URL routing
│   ├── admin.py              # Django admin
│   ├── utils.py              # Utility functions
│   ├── permissions.py        # Permission decorators
│   └── context_processors.py # Template context
├── billingpixel/             # Django project settings
├── theme/                    # Tailwind CSS theme
│   ├── static_src/           # Source files
│   │   ├── src/              # CSS source
│   │   ├── package.json      # Node dependencies
│   │   └── postcss.config.js # PostCSS config
│   └── templates/            # Base templates
├── docker/                   # Docker configurations
│   └── nginx/                # Nginx configs
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker Compose config
├── Dockerfile               # Docker image definition
└── manage.py                # Django management script
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket
```

### Company Setup

After logging in, users can set up their company with:
- Company information and contact details
- Custom branding (logo, colors)
- Document prefixes and numbering
- Default tax rates and payment terms

## 🔐 Security Features

- **Role-Based Access Control**: Four permission levels
- **Secure PDF Downloads**: Token-based authentication
- **Audit Logging**: Complete activity tracking
- **CSRF Protection**: Django built-in security
- **Rate Limiting**: Nginx-based request limiting
- **Input Validation**: Comprehensive form validation

## 🎨 Customization

### Theming
- Company-specific color schemes
- Dynamic CSS variable injection
- Custom logo support
- Responsive design with Tailwind CSS

### Document Templates
- Customizable PDF templates
- Company branding integration
- Multi-language support ready
- Print-optimized layouts

## 📊 API Documentation

### Authentication
All API endpoints require authentication via Django sessions or API tokens.

### Key Endpoints
- `GET /api/clients/` - List company clients
- `GET /api/dashboard-stats/` - Dashboard statistics
- `POST /pdf/invoice/<id>/` - Generate invoice PDF
- `GET /download/<token>/` - Download PDF with token

## 🔄 Background Tasks

### Celery Tasks
- **PDF Cleanup**: Automatic removal of expired PDFs
- **Email Notifications**: Asynchronous email sending
- **Report Generation**: Large report processing

### Scheduled Tasks
- Daily PDF cleanup
- Weekly usage reports
- Monthly subscription processing

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure email settings
- [ ] Set up SSL certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring

### Performance Optimization
- Redis caching enabled
- Static file compression
- Database query optimization
- PDF generation optimization
- Background task processing

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 Management Commands

```bash
# Seed sample data
python manage.py seed_data

# Clean up expired PDFs
python manage.py cleanup_pdfs

# Create sample companies
python manage.py seed_data --companies 5
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
- **PDF Generation Errors**: Check WeasyPrint dependencies
- **Static Files**: Run `collectstatic` after changes
- **Database Issues**: Ensure migrations are applied
- **Permission Errors**: Check user roles and company assignment

### Getting Help
- Check the issues section for known problems
- Review the documentation for configuration details
- Contact support for enterprise features

## 🔮 Roadmap

### Upcoming Features
- Mobile application
- Advanced reporting
- Integration APIs
- Subscription billing
- Multi-currency support
- Advanced tax handling

### Version History
- **v1.0.0**: Initial release with core features
- **v1.1.0**: PDF generation and multi-tenancy
- **v1.2.0**: Role-based permissions and audit logs

---

**Built with ❤️ using Django, Tailwind CSS, and modern web technologies.**
