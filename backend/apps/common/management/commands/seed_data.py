"""
Management command to seed the database with initial data.

This command follows SOLID principles:
- Single Responsibility: Only handles data seeding
- Open/Closed: Extensible for different seed scenarios
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from apps.organizations.models import Organization, Department
from apps.users.models import Role
from apps.projects.models import Client, Project, ProjectCategory
from apps.time_tracking.models import TimeEntry

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with initial data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            default='development',
            help='Seeding mode: development, demo, or production'
        )

    def handle(self, *args, **options):
        mode = options['mode']

        self.stdout.write(
            self.style.SUCCESS(f'Starting data seeding in {mode} mode...')
        )

        # Create roles
        self._create_roles()

        # Create organizations
        org = self._create_organizations()

        # Create users
        users = self._create_users(org)

        # Create departments
        departments = self._create_departments(org, users)

        # Create projects
        self._create_projects(org, departments, users)

        # Create sample time entries if in development mode
        if mode == 'development':
            self._create_sample_time_entries(users)

        self.stdout.write(
            self.style.SUCCESS('Data seeding completed successfully!')
        )

    def _create_roles(self):
        """Create user roles."""
        self.stdout.write('Creating user roles...')

        roles_data = [
            ('employee', 'Employee'),
            ('contractor', 'Contractor'),
            ('team_lead', 'Team Lead'),
            ('manager', 'Manager'),
            ('admin', 'Admin'),
            ('client_admin', 'Client Admin'),
            ('global_admin', 'Global Admin'),
        ]

        for role_name, role_display in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': f'{role_display} role'}
            )
            if created:
                self.stdout.write(f'  Created role: {role_display}')

    def _create_organizations(self):
        """Create sample organizations."""
        self.stdout.write('Creating organizations...')

        org, created = Organization.objects.get_or_create(
            slug='techcorp',
            defaults={
                'name': 'TechCorp Inc.',
                'description': 'A leading technology company',
                'email': 'admin@techcorp.com',
                'phone': '+1-555-0123',
                'website': 'https://techcorp.com',
                'timezone': 'America/New_York',
                'currency': 'USD',
                'subscription_plan': 'professional',
                'max_users': 100,
            }
        )

        if created:
            self.stdout.write('  Created organization: TechCorp Inc.')

        return org

    def _create_users(self, organization):
        """Create sample users."""
        self.stdout.write('Creating users...')

        users_data = [
            {
                'email': 'admin@techcorp.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'employee_id': 'ADMIN001',
                'hourly_rate': 75.00,
            },
            {
                'email': 'manager@techcorp.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'manager',
                'employee_id': 'MGR001',
                'hourly_rate': 65.00,
            },
            {
                'email': 'employee@techcorp.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'employee',
                'employee_id': 'EMP001',
                'hourly_rate': 45.00,
            },
            {
                'email': 'contractor@techcorp.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'contractor',
                'employee_id': 'CON001',
                'hourly_rate': 55.00,
            },
        ]

        created_users = []
        for user_data in users_data:
            role = Role.objects.get(name=user_data.pop('role'))

            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    **user_data,
                    'organization': organization,
                    'role': role,
                    'hire_date': date.today() - timedelta(days=365),
                    'is_active': True,
                }
            )

            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Created user: {user.get_full_name()}')

            created_users.append(user)

        return created_users

    def _create_departments(self, organization, users):
        """Create sample departments."""
        self.stdout.write('Creating departments...')

        # Find manager
        manager = next((u for u in users if u.role.name == 'manager'), None)

        departments_data = [
            {
                'name': 'Engineering',
                'description': 'Software development and engineering',
                'code': 'ENG',
                'manager': manager,
            },
            {
                'name': 'Marketing',
                'description': 'Marketing and business development',
                'code': 'MKT',
            },
            {
                'name': 'Human Resources',
                'description': 'Human resources and administration',
                'code': 'HR',
            },
        ]

        created_departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                organization=organization,
                name=dept_data['name'],
                defaults=dept_data
            )

            if created:
                self.stdout.write(f'  Created department: {dept.name}')

            created_departments.append(dept)

        # Assign users to departments
        if created_departments:
            for user in users:
                if not user.department:
                    if user.role.name in ['employee', 'contractor']:
                        user.department = created_departments[0]  # Engineering
                    elif user.role.name == 'manager':
                        user.department = created_departments[0]  # Engineering
                    else:
                        user.department = created_departments[2]  # HR
                    user.save()

        return created_departments

    def _create_projects(self, organization, departments, users):
        """Create sample projects."""
        self.stdout.write('Creating projects...')

        # Create client
        client, created = Client.objects.get_or_create(
            organization=organization,
            name='Acme Corporation',
            defaults={
                'email': 'contact@acme.com',
                'phone': '+1-555-0199',
                'billing_rate': 120.00,
                'currency': 'USD',
            }
        )

        # Create project category
        category, created = ProjectCategory.objects.get_or_create(
            organization=organization,
            name='Web Development',
            defaults={
                'description': 'Web application development projects',
                'color': '#3B82F6',
            }
        )

        # Create projects
        projects_data = [
            {
                'name': 'Website Redesign',
                'description': 'Complete redesign of the company website',
                'code': 'WEB001',
                'client': client,
                'category': category,
                'budget_hours': 200,
                'budget_amount': 24000.00,
                'hourly_rate': 120.00,
                'is_billable': True,
                'status': 'active',
                'priority': 'high',
            },
            {
                'name': 'Mobile App Development',
                'description': 'Native mobile application for iOS and Android',
                'code': 'MOB001',
                'client': client,
                'category': category,
                'budget_hours': 500,
                'budget_amount': 60000.00,
                'hourly_rate': 120.00,
                'is_billable': True,
                'status': 'active',
                'priority': 'medium',
            },
            {
                'name': 'Internal Tools',
                'description': 'Development of internal productivity tools',
                'code': 'INT001',
                'budget_hours': 100,
                'is_billable': False,
                'status': 'active',
                'priority': 'low',
            },
        ]

        manager = next((u for u in users if u.role.name == 'manager'), None)
        engineering_dept = next((d for d in departments if d.name == 'Engineering'), None)

        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                organization=organization,
                name=project_data['name'],
                defaults={
                    **project_data,
                    'department': engineering_dept,
                    'project_manager': manager,
                    'start_date': date.today() - timedelta(days=30),
                    'end_date': date.today() + timedelta(days=90),
                }
            )

            if created:
                self.stdout.write(f'  Created project: {project.name}')

    def _create_sample_time_entries(self, users):
        """Create sample time entries for development."""
        self.stdout.write('Creating sample time entries...')

        # Get employee and contractor
        employee = next((u for u in users if u.role.name == 'employee'), None)
        contractor = next((u for u in users if u.role.name == 'contractor'), None)

        if not employee:
            return

        # Get projects
        projects = Project.objects.filter(organization=employee.organization)
        if not projects.exists():
            return

        project = projects.first()

        # Create time entries for the last 7 days
        for i in range(7):
            entry_date = date.today() - timedelta(days=i)
            clock_in_time = timezone.now().replace(
                year=entry_date.year,
                month=entry_date.month,
                day=entry_date.day,
                hour=9,
                minute=0,
                second=0,
                microsecond=0
            ) - timedelta(days=i)

            clock_out_time = clock_in_time + timedelta(hours=8, minutes=30)

            time_entry, created = TimeEntry.objects.get_or_create(
                user=employee,
                organization=employee.organization,
                date=entry_date,
                defaults={
                    'project': project,
                    'department': employee.department,
                    'clock_in': clock_in_time,
                    'clock_out': clock_out_time,
                    'description': f'Development work on {project.name}',
                    'is_billable': project.is_billable,
                    'hourly_rate': employee.hourly_rate,
                    'status': 'approved',
                }
            )

            if created:
                self.stdout.write(f'  Created time entry for {entry_date}')

        self.stdout.write('Sample time entries created!')