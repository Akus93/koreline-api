from django.contrib import admin
from koreline.models import UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification, Message,\
    Comment, ReportedComment


class ReportedCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'comment', 'is_pending', 'create_date')
    search_fields = ['author']
    list_filter = ['is_pending']
    list_select_related = ['comment', 'author']
    list_per_page = 25

admin.site.register([UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification, Message, Comment])

admin.site.register(ReportedComment, ReportedCommentAdmin)
