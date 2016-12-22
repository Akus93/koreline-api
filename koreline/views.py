from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, DestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend
from uuid import uuid4
from datetime import timedelta, datetime
from django.db.models import Q

from koreline.permissions import IsOwnerOrReadOnlyForUserProfile, IsOwnerOrReadOnlyForLesson,\
    IsTeacherOrStudentForLessonMembership, IsTeacher
from koreline.serializers import UserProfileSerializer, LessonSerializer, LessonMembershipSerializer, RoomSerializer, \
    NotificationSerializer, MessageSerializer, LastMessageSerializer
from koreline.models import UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification, Message
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
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(lessonmembership__student__user=self.request.user)


class LeaveLessonView(APIView):
    """Opuszczenie lekcji przez ucznia"""
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
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)


class LessonStudentsListView(APIView):
    """Lista uczniow danej lekcji"""
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


class UnsubscribeStudentFromLessonView(APIView):
    """Wydalenie ucznia z lekcji"""
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request, format=None):

        slug = request.data.get('lesson', '')
        username = request.data.get('username', '')

        try:
            student = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            lesson_membership = LessonMembership.objects.get(lesson__teacher__user=request.user, lesson__slug=slug,
                                                             student=student)
        except LessonMembership.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        lesson_membership.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class OpenConversationRoomView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request, format=None):
        """Open room"""

        slug = request.data.get('lesson', '')
        username = request.data.get('student', '')

        try:
            student = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            lesson = Lesson.objects.get(slug=slug)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if lesson.teacher.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if not LessonMembership.objects.filter(lesson=lesson, student=student).exists():
            return Response({'error': 'Ten uczeń nie należy do tej lekcji.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            room = Room.objects.get(lesson=lesson, student=student, is_open=True)
        except Room.DoesNotExist:
            new_key = str(uuid4()).replace('-', '')
            room = Room(lesson=lesson, student=student, key=new_key)
            room.save()

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)


class ConversationRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, key, format=None):

        try:
            conversation_room = Room.objects.select_related('student__user', 'lesson__teacher__user').get(key=key)
        except Room.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if conversation_room.student.user == request.user or conversation_room.lesson.teacher.user == request.user:
            return Response(RoomSerializer(conversation_room).data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        time_threshold = datetime.now() - timedelta(hours=12)
        notifications = Notification.objects.filter(user=request.user.userprofile, is_read=False,
                                                    create_date__gt=time_threshold)
        return Response(NotificationSerializer(notifications, many=True).data, status=status.HTTP_200_OK)


class MessagesWithUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username, format=None):
        """Zwraca wszystkie wiadomości z podanym userem"""
        current_user = request.user.userprofile
        try:
            other_user = UserProfile.objects.select_related('user').get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        messages = Message.objects.filter(Q(sender=current_user) | Q(reciver=current_user),
                                          Q(sender=other_user) | Q(reciver=other_user))
        return Response(MessageSerializer(messages, many=True).data, status=status.HTTP_200_OK)


class MessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """Tworzy nową wiadomość"""

        reciver = request.data.get('reciver', '')
        text = request.data.get('text', '')

        serializer = MessageSerializer(data={'reciver_save': reciver,
                                             'sender_save': request.user.username,
                                             'text': text})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """Zwraca listę osób z ktorymi prowadziliśmy konwersację"""
        current_user = request.user.userprofile
        users = UserProfile.objects.select_related('user')\
                                   .filter(Q(senders__reciver=current_user) | Q(recivers__sender=current_user))\
                                   .order_by('user__first_name')\
                                   .distinct()
        messages = []
        for user in users:
            last_message = Message.objects.filter(Q(sender=current_user) | Q(reciver=current_user),
                                                  Q(sender=user) | Q(reciver=user)).first()
            messages.append({'user': user, 'message': last_message})
        return Response(LastMessageSerializer(messages, many=True).data, status=status.HTTP_200_OK)
