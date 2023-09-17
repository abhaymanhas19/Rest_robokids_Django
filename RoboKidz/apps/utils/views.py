from django.shortcuts import render
from .serializers import *
from .models import *

# Create your views here.
from rest_framework import permissions
from rest_framework import viewsets


class ISUserRegistration(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        else:
            return bool(request.user and request.user.is_authenticated)


class IsOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user


class FollowAPIView(viewsets.ModelViewSet):
    serializer_class = serializers.FollowRequestSerializer
    queryset = models.FollowRequest.objects.all()
