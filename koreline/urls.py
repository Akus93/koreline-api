from django.conf.urls import url

from koreline.views import CurrentUserView


urlpatterns = [
    url(r'^user/$', CurrentUserView.as_view(), name='current-user'),
]
