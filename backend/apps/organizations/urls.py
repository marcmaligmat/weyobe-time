from django.urls import path
from . import views

urlpatterns = [
    path('current/', views.OrganizationDetailView.as_view(), name='current-organization'),
    path('departments/', views.DepartmentListCreateView.as_view(), name='department-list-create'),
    path('departments/<uuid:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
]