from django.contrib import admin
from django.conf.urls import url, include


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('koreline.urls')),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
]
