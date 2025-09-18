"""
Celery configuration for TimeTracker project.

This module provides Celery configuration that follows SOLID principles:
- Single Responsibility: Only handles Celery configuration
- Open/Closed: Extensible through environment variables
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('timetracker')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule
app.conf.beat_schedule = {
    'check-overtime-violations': {
        'task': 'apps.compliance.tasks.check_overtime_violations',
        'schedule': 60.0,  # Every minute
    },
    'send-break-reminders': {
        'task': 'apps.compliance.tasks.send_break_reminders',
        'schedule': 900.0,  # Every 15 minutes
    },
    'process-timesheet-periods': {
        'task': 'apps.time_tracking.tasks.process_timesheet_periods',
        'schedule': 3600.0,  # Every hour
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')