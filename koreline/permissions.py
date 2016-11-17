from rest_framework.compat import is_authenticated
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnlyForUserProfile(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.teacher.user == request.user


class IsOwnerOrReadOnlyForLesson(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.teacher.user == request.user

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user and is_authenticated(request.user)


