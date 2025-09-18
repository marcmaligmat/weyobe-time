from rest_framework import generics, permissions
from .models import Project, Client, ProjectCategory
from .serializers import ProjectSerializer, ClientSerializer, ProjectCategorySerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False
        )


class ClientListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)