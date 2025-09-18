from django.urls import path
from . import views

urlpatterns = [
    # User CRUD operations
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),

    # Current user operations
    path('me/', views.current_user, name='current-user'),
    path('me/profile/', views.update_profile, name='update-profile'),
    path('me/compliance/', views.update_compliance_settings, name='update-compliance'),
    path('me/password/', views.change_password, name='change-password'),
    path('me/stats/', views.user_stats, name='current-user-stats'),

    # User statistics
    path('<uuid:user_id>/stats/', views.user_stats, name='user-stats'),
]