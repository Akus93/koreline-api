from rest_framework.compat import is_authenticated
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnlyForUserProfile(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.user == request.user


class IsOwnerOrReadOnlyForLesson(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.teacher.user == request.user

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user and is_authenticated(request.user)


class IsTeacherOrStudentForLessonMembership(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.lesson.teacher.user == request.user or obj.student.user == request.user

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user and is_authenticated(request.user)


class IsTeacher(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.lesson.teacher.user == request.user

    def has_permission(self, request, view):
        return request.user and is_authenticated(request.user) and request.user.userprofile.is_teacher
