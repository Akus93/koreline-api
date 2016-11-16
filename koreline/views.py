from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveUpdateDestroyAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend

from koreline.permissions import IsOwnerOrReadOnlyForUserProfile, IsOwnerOrReadOnlyForLesson
from koreline.serializers import UserProfileSerializer, LessonSerializer
from koreline.models import UserProfile, Lesson
from koreline.filters import LessonFilter
from koreline.throttles import LessonThrottle


class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnlyForUserProfile]
    http_method_names = ['get', 'patch', 'head', 'delete']
    lookup_field = 'user__username'


class LessonViewSet(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyForLesson]
    # throttle_classes = (LessonThrottle, ) # TODO odkomentowac po testach
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend,)
    filter_class = LessonFilter

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.userprofile)


class CurrentUserView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnlyForUserProfile]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
