from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from koreline.views import UserProfileViewSet, LessonViewSet, CurrentUserView, SubjectsView, StagesView,\
                           LessonStudentsListView, JoinToLessonView, StudentLessonsListView, LeaveLessonView,\
                           UnsubscribeStudentFromLessonView


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

    url(r'subjects/$', SubjectsView.as_view()),
    url(r'stages/$', StagesView.as_view()),

    url(r'^', include(router.urls)),
]
