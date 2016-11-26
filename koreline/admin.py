from django.contrib import admin
from koreline.models import UserProfile, Lesson, Subject, Stage, LessonMembership


admin.site.register([UserProfile, Lesson, Subject, Stage, LessonMembership])

