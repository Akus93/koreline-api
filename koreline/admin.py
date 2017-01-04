from django.contrib import admin
from koreline.models import UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification, Message,\
    Comment, RaportedComment

admin.site.register([UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification, Message, Comment,
                     RaportedComment])

