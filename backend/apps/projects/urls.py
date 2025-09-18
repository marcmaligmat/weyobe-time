from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<uuid:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('clients/', views.ClientListCreateView.as_view(), name='client-list-create'),
]