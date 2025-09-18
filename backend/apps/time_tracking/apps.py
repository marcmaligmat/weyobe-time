from django.apps import AppConfig


class TimeTrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.time_tracking'
    verbose_name = 'Time Tracking'