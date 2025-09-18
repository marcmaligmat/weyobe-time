from rest_framework import generics, permissions
from .models import ComplianceAlert
from rest_framework import serializers


class ComplianceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceAlert
        fields = '__all__'
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']


class ComplianceAlertListView(generics.ListAPIView):
    serializer_class = ComplianceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ComplianceAlert.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False
        )