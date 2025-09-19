"""
Compliance-related Celery tasks for the TimeTracker application.

This module provides background tasks for:
- Overtime violation checking
- Break reminder notifications
- Compliance report generation
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_overtime_violations():
    """
    Check for overtime violations across all organizations.

    This task runs periodically to identify users who may be
    working excessive hours and trigger compliance alerts.
    """
    try:
        logger.info("Starting overtime violations check...")

        # Import here to avoid circular imports
        from apps.time_tracking.models import TimeEntry
        from apps.users.models import User
        from datetime import timedelta

        # Get current date and week boundaries
        now = timezone.now()
        week_start = now - timedelta(days=now.weekday())

        # Find users with potential overtime violations
        overtime_users = []

        # This is a basic implementation - you can enhance with more complex logic
        users = User.objects.filter(is_active=True)

        for user in users:
            # Calculate total hours for current week
            week_entries = TimeEntry.objects.filter(
                user=user,
                clock_in__gte=week_start,
                clock_in__lt=week_start + timedelta(days=7),
                clock_out__isnull=False
            )

            total_hours = sum([
                (entry.clock_out - entry.clock_in).total_seconds() / 3600
                for entry in week_entries
            ])

            # Check if exceeds 40 hours (configurable threshold)
            if total_hours > 40:
                overtime_users.append({
                    'user': user,
                    'total_hours': total_hours,
                    'overtime_hours': total_hours - 40
                })

        if overtime_users:
            logger.warning(f"Found {len(overtime_users)} users with potential overtime violations")
            # You can add notification logic here
        else:
            logger.info("No overtime violations found")

        return f"Checked overtime for {users.count()} users. Found {len(overtime_users)} violations."

    except Exception as e:
        logger.error(f"Error checking overtime violations: {str(e)}")
        raise


@shared_task
def send_break_reminders():
    """
    Send break reminders to users who have been working for extended periods.

    This task identifies users with active time entries that have been
    running for a long time without breaks.
    """
    try:
        logger.info("Starting break reminders check...")

        # Import here to avoid circular imports
        from apps.time_tracking.models import TimeEntry
        from datetime import timedelta

        # Get current time
        now = timezone.now()

        # Find active time entries that have been running for more than 4 hours
        cutoff_time = now - timedelta(hours=4)

        long_entries = TimeEntry.objects.filter(
            clock_in__lt=cutoff_time,
            clock_out__isnull=True,  # Still active
            user__is_active=True
        ).select_related('user')

        reminder_count = 0

        for entry in long_entries:
            duration = now - entry.clock_in
            hours_worked = duration.total_seconds() / 3600

            logger.info(f"Sending break reminder to {entry.user.email} (worked {hours_worked:.1f} hours)")

            # Send email reminder (you can enhance this with proper templates)
            try:
                send_mail(
                    subject='Break Reminder - TimeTracker',
                    message=f'Hi {entry.user.first_name},\n\n'
                           f'You have been working for {hours_worked:.1f} hours. '
                           f'Consider taking a break to maintain productivity and well-being.\n\n'
                           f'Best regards,\nTimeTracker Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[entry.user.email],
                    fail_silently=False
                )
                reminder_count += 1
            except Exception as email_error:
                logger.error(f"Failed to send break reminder to {entry.user.email}: {str(email_error)}")

        logger.info(f"Sent {reminder_count} break reminders")
        return f"Sent {reminder_count} break reminders to users working extended hours"

    except Exception as e:
        logger.error(f"Error sending break reminders: {str(e)}")
        raise


@shared_task
def generate_compliance_report():
    """
    Generate periodic compliance reports for organizations.

    This task creates summary reports of compliance metrics
    and can be used for audit purposes.
    """
    try:
        logger.info("Starting compliance report generation...")

        # Import here to avoid circular imports
        from apps.organizations.models import Organization
        from apps.time_tracking.models import TimeEntry
        from datetime import timedelta

        # Get last week's data
        now = timezone.now()
        week_end = now - timedelta(days=now.weekday())
        week_start = week_end - timedelta(days=7)

        reports_generated = 0

        for org in Organization.objects.filter(is_active=True):
            # Generate compliance metrics for the organization
            entries = TimeEntry.objects.filter(
                organization=org,
                clock_in__gte=week_start,
                clock_in__lt=week_end,
                clock_out__isnull=False
            )

            # Calculate compliance metrics
            total_entries = entries.count()
            total_hours = sum([
                (entry.clock_out - entry.clock_in).total_seconds() / 3600
                for entry in entries
            ])

            # You can expand this with more detailed compliance checks
            compliance_data = {
                'organization': org.name,
                'period': f"{week_start.date()} to {week_end.date()}",
                'total_entries': total_entries,
                'total_hours': round(total_hours, 2),
                'average_daily_hours': round(total_hours / 7, 2) if total_hours > 0 else 0,
            }

            logger.info(f"Generated compliance report for {org.name}: {compliance_data}")
            reports_generated += 1

        return f"Generated compliance reports for {reports_generated} organizations"

    except Exception as e:
        logger.error(f"Error generating compliance reports: {str(e)}")
        raise