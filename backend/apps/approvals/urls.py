from django.urls import path
from . import views

urlpatterns = [
    path('workflows/', views.ApprovalWorkflowListView.as_view(), name='approval-workflows'),
]