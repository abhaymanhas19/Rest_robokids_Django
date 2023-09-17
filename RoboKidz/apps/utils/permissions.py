from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated


class IsCurrentUserOwnerOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.created_by == request.user
