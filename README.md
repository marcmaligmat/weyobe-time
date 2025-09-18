# TimeTracker Pro - Complete Time Tracking Solution

A modern, full-stack time tracking application built with Next.js and Django, following SOLID principles throughout. This Clockify clone provides comprehensive time tracking, project management, compliance monitoring, and role-based access control.

## Features

### Frontend (Next.js 14 + TypeScript)
- **Modern Time Tracking Interface** with prominent timer widget
- **Role-based Dashboards** for all user types (Employee, Contractor, Team Lead, Manager, Admin, Client Admin, Global Admin)
- **Real-time Timer** with break management and project allocation
- **Responsive Design** with shadcn/ui components
- **State Management** with Zustand
- **Authentication** with NextAuth.js integration ready

### Backend (Django REST Framework)
- **Multi-tenant Architecture** with organization-level isolation
- **SOLID Principles** implementation throughout
- **Role-based Permissions System** with fine-grained access control
- **Time Tracking APIs** with clock in/out, breaks, and manual entries
- **Project Management** with hierarchical departments and client billing
- **Compliance Monitoring** with overtime alerts and break reminders
- **Approval Workflows** for time modifications and overtime
- **Comprehensive Reporting** with filtering and export capabilities

## Technology Stack

### Frontend
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Zustand for state management
- React Hook Form with Zod validation
- Lucide React icons
- Recharts for analytics

### Backend
- Django 4.2 + Django REST Framework
- PostgreSQL database
- Redis for caching and sessions
- Celery for background tasks
- JWT authentication
- Docker Compose orchestration

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd time-tracker
```

### 2. Backend Setup

#### Using Docker (Recommended)
```bash
cd backend
cp .env.example .env
docker-compose up --build
```

#### Manual Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env

# Set up database
python manage.py migrate
python manage.py seed_data --mode development
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

### Demo Credentials
```
Admin: admin@techcorp.com / password123
Manager: manager@techcorp.com / password123
Employee: employee@techcorp.com / password123
Contractor: contractor@techcorp.com / password123
```

## Project Structure

```
time-tracker/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── lib/            # Utilities and stores
│   │   └── types/          # TypeScript definitions
│   └── package.json
├── backend/                 # Django backend application
│   ├── apps/               # Django applications
│   │   ├── common/         # Shared utilities and base models
│   │   ├── organizations/  # Multi-tenant organization management
│   │   ├── users/          # User authentication and profiles
│   │   ├── time_tracking/  # Core time tracking functionality
│   │   ├── projects/       # Project and client management
│   │   ├── compliance/     # Compliance monitoring and alerts
│   │   ├── approvals/      # Approval workflow management
│   │   └── reports/        # Reporting and analytics
│   ├── config/             # Django settings and configuration
│   └── requirements.txt
└── README.md
```

## Architecture Highlights

### SOLID Principles Implementation

#### Single Responsibility Principle
- Each model handles one specific domain concept
- Views focus on single operations (CRUD, authentication, etc.)
- Serializers handle only data transformation
- Services handle specific business logic

#### Open/Closed Principle
- Base models can be extended without modification
- Serializers use inheritance for different use cases
- Settings are configurable through environment variables
- Middleware and permissions are pluggable

#### Liskov Substitution Principle
- Abstract base models can be substituted by concrete implementations
- Permission classes follow consistent interfaces
- Serializers maintain contract compatibility

#### Interface Segregation Principle
- Focused serializers for different API operations
- Role-specific permissions and viewsets
- Separate concerns for different user types

#### Dependency Inversion Principle
- Abstract base classes define contracts
- Dependency injection through Django's DI container
- Configuration through environment variables

### Multi-Tenant Architecture
- Organization-scoped models with proper isolation
- Middleware-based tenant resolution
- Role-based access control within organizations
- Hierarchical department and project structure

### Time Tracking Features
- Real-time clock in/out with location tracking
- Multiple break types (short break, lunch, personal)
- Manual time entry with validation
- Automatic overtime calculation
- Break compliance monitoring
- Project time allocation and billing

### Security Features
- JWT-based authentication
- Role-based access control
- Organization-level data isolation
- Session tracking and management
- Input validation and sanitization
- CORS protection

## API Documentation

### Authentication Endpoints
```
POST /api/v1/auth/login/          # Login with email/password
POST /api/v1/auth/refresh/        # Refresh JWT token
POST /api/v1/auth/verify/         # Verify JWT token
```

### Time Tracking Endpoints
```
GET  /api/v1/time-tracking/entries/              # List time entries
POST /api/v1/time-tracking/entries/              # Create time entry
GET  /api/v1/time-tracking/entries/{id}/         # Get time entry details
PUT  /api/v1/time-tracking/entries/{id}/         # Update time entry

POST /api/v1/time-tracking/clock-in/             # Clock in
POST /api/v1/time-tracking/clock-out/            # Clock out
POST /api/v1/time-tracking/entries/{id}/start-break/  # Start break
POST /api/v1/time-tracking/entries/{id}/end-break/    # End break

GET  /api/v1/time-tracking/current/              # Current active entry
GET  /api/v1/time-tracking/summary/              # Time summary
```

### User Management Endpoints
```
GET  /api/v1/users/                    # List users
POST /api/v1/users/                    # Create user
GET  /api/v1/users/{id}/               # Get user details
PUT  /api/v1/users/{id}/               # Update user

GET  /api/v1/users/me/                 # Current user profile
PUT  /api/v1/users/me/profile/         # Update profile
PUT  /api/v1/users/me/compliance/      # Update compliance settings
POST /api/v1/users/me/password/        # Change password
```

### Project Management Endpoints
```
GET  /api/v1/projects/                 # List projects
POST /api/v1/projects/                 # Create project
GET  /api/v1/projects/{id}/            # Get project details
PUT  /api/v1/projects/{id}/            # Update project

GET  /api/v1/projects/clients/         # List clients
POST /api/v1/projects/clients/         # Create client
```

## Development

### Running Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
cd backend
flake8 .
black .
isort .

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

### Database Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Seed Data
```bash
cd backend
python manage.py seed_data --mode development
```

## Deployment

### Docker Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production settings
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

#### Backend (.env)
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/timetracker
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

## Contributing

1. Follow SOLID principles in all code
2. Write comprehensive tests
3. Use TypeScript strictly in frontend
4. Follow Django best practices in backend
5. Update documentation for new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issues for bugs
- Check documentation for setup help
- Review API documentation for integration

---

Built with ❤️ using modern web technologies and SOLID principles.