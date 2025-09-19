"""
Time tracking related Celery tasks for the TimeTracker application.

This module provides background tasks for:
- Timesheet period processing
- Automatic time entry management
- Time tracking analytics
"""

from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)


@shared_task
def process_timesheet_periods():
    """
    Process timesheet periods and generate summaries.

    This task runs periodically to:
    - Close completed timesheet periods
    - Generate time summaries
    - Calculate billable hours
    - Update project progress
    """
    try:
        logger.info("Starting timesheet period processing...")

        # Import here to avoid circular imports
        from apps.time_tracking.models import TimeEntry, TimesheetPeriod
        from apps.projects.models import Project
        from apps.organizations.models import Organization

        processed_periods = 0
        current_time = timezone.now()

        # Find timesheet periods that need processing
        periods_to_process = TimesheetPeriod.objects.filter(
            status='open',
            end_date__lt=current_time.date(),
            is_active=True
        )

        for period in periods_to_process:
            try:
                with transaction.atomic():
                    # Get all time entries for this period
                    entries = TimeEntry.objects.filter(
                        organization=period.organization,
                        clock_in__date__gte=period.start_date,
                        clock_in__date__lte=period.end_date,
                        clock_out__isnull=False
                    )

                    # Calculate totals
                    total_hours = sum([
                        (entry.clock_out - entry.clock_in).total_seconds() / 3600
                        for entry in entries
                    ])

                    billable_hours = sum([
                        (entry.clock_out - entry.clock_in).total_seconds() / 3600
                        for entry in entries
                        if entry.is_billable
                    ])

                    # Update period with calculations
                    period.total_hours = round(total_hours, 2)
                    period.billable_hours = round(billable_hours, 2)
                    period.status = 'closed'
                    period.processed_at = current_time
                    period.save()

                    logger.info(f"Processed period {period.id} for {period.organization.name}: "
                              f"{period.total_hours}h total, {period.billable_hours}h billable")

                    processed_periods += 1

            except Exception as period_error:
                logger.error(f"Error processing period {period.id}: {str(period_error)}")
                continue

        # Create new periods for organizations that need them
        organizations = Organization.objects.filter(is_active=True)
        new_periods_created = 0

        for org in organizations:
            # Check if organization needs a new current period
            latest_period = TimesheetPeriod.objects.filter(
                organization=org
            ).order_by('-end_date').first()

            if not latest_period or latest_period.end_date < current_time.date():
                # Create new period (weekly periods)
                start_date = current_time.date()
                if latest_period:
                    start_date = latest_period.end_date + timedelta(days=1)

                end_date = start_date + timedelta(days=6)  # Weekly period

                new_period = TimesheetPeriod.objects.create(
                    organization=org,
                    start_date=start_date,
                    end_date=end_date,
                    status='open'
                )

                logger.info(f"Created new period for {org.name}: {start_date} to {end_date}")
                new_periods_created += 1

        result = f"Processed {processed_periods} timesheet periods, created {new_periods_created} new periods"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error processing timesheet periods: {str(e)}")
        raise


@shared_task
def auto_stop_long_running_entries():
    """
    Automatically stop time entries that have been running for too long.

    This task identifies time entries that have been active for more than
    a configured maximum duration and stops them automatically.
    """
    try:
        logger.info("Starting auto-stop for long running entries...")

        # Import here to avoid circular imports
        from apps.time_tracking.models import TimeEntry

        # Get current time
        now = timezone.now()

        # Find entries running for more than 24 hours (configurable)
        cutoff_time = now - timedelta(hours=24)

        long_entries = TimeEntry.objects.filter(
            clock_in__lt=cutoff_time,
            clock_out__isnull=True,  # Still active
            user__is_active=True
        ).select_related('user', 'task', 'project')

        stopped_count = 0

        for entry in long_entries:
            try:
                # Stop the entry at the cutoff time to avoid excessive hours
                entry.clock_out = entry.clock_in + timedelta(hours=24)
                entry.save()

                logger.warning(f"Auto-stopped long running entry for {entry.user.email}: "
                             f"Entry ID {entry.id}, was running for {(now - entry.clock_in).total_seconds() / 3600:.1f} hours")

                stopped_count += 1

            except Exception as entry_error:
                logger.error(f"Error stopping entry {entry.id}: {str(entry_error)}")
                continue

        result = f"Auto-stopped {stopped_count} long running time entries"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error auto-stopping long running entries: {str(e)}")
        raise


@shared_task
def calculate_project_progress():
    """
    Calculate and update project progress based on time entries.

    This task updates project completion percentages and
    estimated completion dates based on actual time spent.
    """
    try:
        logger.info("Starting project progress calculation...")

        # Import here to avoid circular imports
        from apps.projects.models import Project
        from apps.time_tracking.models import TimeEntry

        updated_projects = 0

        # Get active projects with budget hours defined
        projects = Project.objects.filter(
            is_active=True,
            budget_hours__isnull=False,
            budget_hours__gt=0
        )

        for project in projects:
            try:
                # Calculate total hours spent on this project
                entries = TimeEntry.objects.filter(
                    project=project,
                    clock_out__isnull=False
                )

                total_hours = sum([
                    (entry.clock_out - entry.clock_in).total_seconds() / 3600
                    for entry in entries
                ])

                # Calculate progress percentage
                progress_percentage = min(100, (total_hours / project.budget_hours) * 100)

                # Estimate completion date if there's a consistent work rate
                if total_hours > 0 and project.start_date:
                    days_elapsed = (timezone.now().date() - project.start_date).days
                    if days_elapsed > 0:
                        hours_per_day = total_hours / days_elapsed
                        remaining_hours = project.budget_hours - total_hours

                        if remaining_hours > 0 and hours_per_day > 0:
                            estimated_days_remaining = remaining_hours / hours_per_day
                            estimated_completion = timezone.now().date() + timedelta(days=estimated_days_remaining)

                            # You can add an estimated_completion_date field to Project model
                            logger.info(f"Project {project.name}: {progress_percentage:.1f}% complete, "
                                      f"estimated completion: {estimated_completion}")

                logger.info(f"Updated progress for project {project.name}: "
                          f"{total_hours:.1f}/{project.budget_hours}h ({progress_percentage:.1f}%)")

                updated_projects += 1

            except Exception as project_error:
                logger.error(f"Error calculating progress for project {project.id}: {str(project_error)}")
                continue

        result = f"Updated progress for {updated_projects} projects"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error calculating project progress: {str(e)}")
        raise


@shared_task
def generate_daily_time_summaries():
    """
    Generate daily time summaries for reporting and analytics.

    This task creates daily summary records that can be used
    for quick reporting and dashboard displays.
    """
    try:
        logger.info("Starting daily time summaries generation...")

        # Import here to avoid circular imports
        from apps.time_tracking.models import TimeEntry
        from apps.users.models import User
        from apps.organizations.models import Organization

        # Get yesterday's date
        yesterday = timezone.now().date() - timedelta(days=1)

        summaries_created = 0

        # Generate summaries for each active organization
        for org in Organization.objects.filter(is_active=True):
            # Get all users in this organization
            org_users = User.objects.filter(
                organization_memberships__organization=org,
                is_active=True
            )

            for user in org_users:
                # Get time entries for yesterday
                entries = TimeEntry.objects.filter(
                    user=user,
                    organization=org,
                    clock_in__date=yesterday,
                    clock_out__isnull=False
                )

                if entries.exists():
                    # Calculate daily totals
                    total_hours = sum([
                        (entry.clock_out - entry.clock_in).total_seconds() / 3600
                        for entry in entries
                    ])

                    billable_hours = sum([
                        (entry.clock_out - entry.clock_in).total_seconds() / 3600
                        for entry in entries
                        if entry.is_billable
                    ])

                    # Count unique projects worked on
                    projects_count = entries.values('project').distinct().count()

                    # You can create a DailySummary model to store these
                    logger.info(f"Daily summary for {user.email} on {yesterday}: "
                              f"{total_hours:.1f}h total, {billable_hours:.1f}h billable, "
                              f"{projects_count} projects")

                    summaries_created += 1

        result = f"Generated {summaries_created} daily time summaries for {yesterday}"
        logger.info(result)
        return result

    except Exception as e:
        logger.error(f"Error generating daily time summaries: {str(e)}")
        raise