from rest_framework.viewsets import ModelViewSet

from koreline.permissions import IsOwnerOrReadOnlyForUserProfile, IsOwnerOrReadOnlyForLesson
from koreline.serializers import UserProfileSerializer, LessonSerializer
from koreline.models import UserProfile, Lesson
from koreline.throttles import LessonThrottle


class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnlyForUserProfile]
    http_method_names = ['get', 'patch', 'head', 'delete']


class LessonViewSet(ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrReadOnlyForLesson]
    # throttle_classes = (LessonThrottle, ) TODO odkomentowac po testach

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.userprofile)
