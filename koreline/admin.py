from django.contrib import admin
from koreline.models import UserProfile, Lesson, Subject


admin.site.register([UserProfile, Lesson, Subject])

