from django.contrib import admin
from koreline.models import UserProfile, Lesson, Subject, Stage


admin.site.register([UserProfile, Lesson, Subject, Stage])

