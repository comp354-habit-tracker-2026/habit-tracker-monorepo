from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Activity
from .serialisers import ActivitySerialiser

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerialiser
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def perform_create(self, serialiser):
        serialiser.save(user=self.request.user)
