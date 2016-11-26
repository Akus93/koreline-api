from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, DestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend

from koreline.permissions import IsOwnerOrReadOnlyForUserProfile, IsOwnerOrReadOnlyForLesson,\
    IsTeacherOrStudentForLessonMembership
from koreline.serializers import UserProfileSerializer, LessonSerializer, LessonMembershipSerializer
from koreline.models import UserProfile, Lesson, Subject, Stage, LessonMembership
from koreline.filters import LessonFilter, LessonMembershipFilter
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
    permission_classes = [IsOwnerOrReadOnlyForLesson]
    # throttle_classes = (LessonThrottle, ) # TODO odkomentowac po testach
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend,)
    filter_class = LessonFilter

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.userprofile)
        user = self.request.user.userprofile
        user.is_teacher = True
        user.save()


class CurrentUserView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnlyForUserProfile]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)


class SubjectsView(APIView):

    def get(self, request, format=None):
        subjects = [subject.name for subject in Subject.objects.all()]
        return Response(subjects)


class StagesView(APIView):

    def get(self, request, format=None):
        stages = [stage.name for stage in Stage.objects.all()]
        return Response(stages)


class JoinToLessonView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        slug = request.data.get('lesson', '')
        try:
            lesson = Lesson.objects.get(slug=slug)
        except Lesson.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if LessonMembership.objects.filter(student=self.request.user.userprofile, lesson=lesson).exists():
            return Response({'error': 'Jesteś już zapisany'}, status=status.HTTP_409_CONFLICT)
        membership = LessonMembership(student=self.request.user.userprofile, lesson=lesson).save()
        return Response(LessonMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)


class StudentLessonsListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonMembershipSerializer

    def get_queryset(self):
        return LessonMembership.objects.filter(student=self.request.user.userprofile)


class LeaveLessonView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        slug = request.data.get('lesson', '')
        try:
            lesson = Lesson.objects.get(slug=slug)
        except Lesson.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not LessonMembership.objects.filter(student=self.request.user.userprofile, lesson=lesson).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        LessonMembership.objects.get(student=self.request.user.userprofile, lesson=lesson).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LessonStudentsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug, format=None):

        try:
            lesson = Lesson.objects.select_related('teacher', 'teacher__user').get(slug=slug)
        except Lesson.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if lesson.teacher.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        memberships = LessonMembership.objects.filter(lesson=lesson)\
                                      .select_related('student', 'lesson', 'lesson__teacher', 'lesson__teacher__user')

        if not memberships:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        students = [UserProfileSerializer(membership.student).data for membership in memberships]
        return Response(students, status=status.HTTP_200_OK)


# class LessonMembershipViewSet(ModelViewSet):
#     queryset = LessonMembership.objects.all()
#     serializer_class = LessonMembershipSerializer
#     permission_classes = [IsTeacherOrStudentForLessonMembership]  # TODO
#     # throttle_classes = (, ) # TODO
#     # lookup_field = 'lesson__slug'
#     filter_backends = (DjangoFilterBackend,)
#     filter_class = LessonMembershipFilter
#
#     # def perform_create(self, serializer):
#     #     serializer.save(teacher=self.request.user.userprofile)
#     #     user = self.request.user.userprofile
#     #     user.is_teacher = True
#     #     user.save()

