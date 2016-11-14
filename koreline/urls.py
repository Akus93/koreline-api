from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from koreline.views import UserProfileViewSet, LessonViewSet, CurrentUserView

router = DefaultRouter()
router.register(r'users', UserProfileViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'user/edit-profile/$', CurrentUserView.as_view()),
]
