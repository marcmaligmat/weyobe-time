from django.urls import path
from . import views

urlpatterns = [
    # Time entries
    path('entries/', views.TimeEntryListCreateView.as_view(), name='time-entry-list-create'),
    path('entries/<uuid:pk>/', views.TimeEntryDetailView.as_view(), name='time-entry-detail'),

    # Clock in/out operations
    path('clock-in/', views.clock_in, name='clock-in'),
    path('clock-out/', views.clock_out, name='clock-out'),

    # Break management
    path('entries/<uuid:time_entry_id>/start-break/', views.start_break, name='start-break'),
    path('entries/<uuid:time_entry_id>/end-break/', views.end_break, name='end-break'),

    # Current status
    path('current/', views.current_time_entry, name='current-time-entry'),
    path('summary/', views.time_summary, name='time-summary'),
]