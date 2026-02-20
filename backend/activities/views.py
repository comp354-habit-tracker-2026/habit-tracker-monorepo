from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Activity
from .serialisers import ActivitySerialiser

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerialiser
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user).order_by('-date', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
