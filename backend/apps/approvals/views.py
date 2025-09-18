from rest_framework import generics, permissions
from .models import ApprovalWorkflow
from rest_framework import serializers


class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalWorkflow
        fields = '__all__'
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class ApprovalWorkflowListView(generics.ListAPIView):
    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApprovalWorkflow.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False
        )