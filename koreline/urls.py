from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from koreline.views import UserProfileViewSet, LessonViewSet, SubjectsView, StagesView,\
                           LessonStudentsListView, JoinToLessonView, StudentLessonsListView, LeaveLessonView,\
                           UnsubscribeStudentFromLessonView, OpenConversationRoomView, ConversationRoomView, \
                           NotificationView, MessagesWithUserView, MessagesView, UnreadMessagesView,\
                           ConversationForLessonView, CreateCommentView, TeacherCommentsView, ReportCommentView,\
                           CloseConversationRoomView, CurrentUserView, BuyTokensView, SellTokensView, TeacherBillView,\
                           StudentBillView, TeacherBillDeleteView

router = DefaultRouter()
router.register(r'users', UserProfileViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [

    url(r'lessons/join/$', JoinToLessonView.as_view()),  # TESTED
    url(r'lessons/leave/$', LeaveLessonView.as_view()),  # TESTED
    url(r'lessons/(?P<slug>[\w-]+)/members/$', LessonStudentsListView.as_view()),  # TESTED

    url(r'teacher/lessons/unsubscribe/$', UnsubscribeStudentFromLessonView.as_view()),  # TESTED
    url(r'teacher/bills/$', TeacherBillView.as_view()),  # TESTED
    url(r'teacher/bills/(?P<pk>\d+)/$', TeacherBillDeleteView.as_view()),

    url(r'user/my-profile/$', CurrentUserView.as_view()),  # TESTED
    url(r'user/my-lessons/$', StudentLessonsListView.as_view()),  # TESTED
    url(r'user/tokens/buy/$', BuyTokensView.as_view()),  # TESTED
    url(r'user/tokens/sell/$', SellTokensView.as_view()),  # TESTED
    url(r'user/bills/$', StudentBillView.as_view()),

    url(r'room/open/$', OpenConversationRoomView.as_view()),  # TESTED
    url(r'room/close/$', CloseConversationRoomView.as_view()),  # TESTED
    url(r'room/lesson/(?P<slug>[\w-]+)/$', ConversationForLessonView.as_view()),  # TESTED
    url(r'room/(?P<key>[\w]+)/$', ConversationRoomView.as_view()),  # TESTED

    url(r'subjects/$', SubjectsView.as_view()),  # TESTED
    url(r'stages/$', StagesView.as_view()),  # TESTED

    url(r'notifications/$', NotificationView.as_view()),

    url(r'messages/unread/$', UnreadMessagesView.as_view()),  # TESTED
    url(r'messages/(?P<username>[\w.]+)/$', MessagesWithUserView.as_view()),  # TESTED
    url(r'messages/$', MessagesView.as_view()),  # TESTED

    url(r'comments/create/$', CreateCommentView.as_view()),  # TESTED
    url(r'comments/report/$', ReportCommentView.as_view()),
    url(r'comments/(?P<teacher>[\w.]+)/$', TeacherCommentsView.as_view()),  # TESTED

    url(r'^', include(router.urls)),
]
