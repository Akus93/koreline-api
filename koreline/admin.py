from django.contrib import admin
from koreline.models import UserProfile, Lesson

admin.site.register([UserProfile, Lesson])

