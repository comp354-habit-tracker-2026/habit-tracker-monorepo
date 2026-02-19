from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Goal
from .serialisers import GoalSerialiser

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerialiser
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serialiser):
        serialiser.save(user=self.request.user)
