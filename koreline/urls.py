from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from koreline.views import UserProfileViewSet, LessonViewSet, CurrentUserView, SubjectsView, StagesView,\
                           LessonStudentsListView, JoinToLessonView, StudentLessonsListView, LeaveLessonView,\
                           UnsubscribeStudentFromLessonView, OpenConversationRoomView, ConversationRoomView, \
                           NotificationView, MessagesWithUserView, MessagesView

router = DefaultRouter()
router.register(r'users', UserProfileViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [

    url(r'lessons/join/$', JoinToLessonView.as_view()),
    url(r'lessons/leave/$', LeaveLessonView.as_view()),
    url(r'lessons/(?P<slug>[\w-]+)/members/$', LessonStudentsListView.as_view()),

    url(r'teacher/lessons/unsubscribe/$', UnsubscribeStudentFromLessonView.as_view()),

    url(r'user/edit-profile/$', CurrentUserView.as_view()),
    url(r'user/my-lessons/$', StudentLessonsListView.as_view()),

    # url(r'teacher/my-lessons/$', TeacherLessonsListView.as_view()),

    url(r'room/open/$', OpenConversationRoomView.as_view()),
    url(r'room/(?P<key>[\w]+)/$', ConversationRoomView.as_view()),

    url(r'subjects/$', SubjectsView.as_view()),
    url(r'stages/$', StagesView.as_view()),

    url(r'notifications/$', NotificationView.as_view()),

    url(r'messages/(?P<username>[\w]+)/$', MessagesWithUserView.as_view()),
    url(r'messages/', MessagesView.as_view()),

    url(r'^', include(router.urls)),
]
