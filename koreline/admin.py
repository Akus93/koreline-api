from django.contrib import admin
from koreline.models import UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification

admin.site.register([UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification])

