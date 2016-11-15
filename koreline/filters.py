from django_filters.rest_framework import FilterSet
from django_filters import CharFilter

from koreline.models import Lesson


class LessonFilter(FilterSet):
    teacher = CharFilter(name='teacher__user__username')

    class Meta:
        model = Lesson
        fields = ['teacher', 'slug']
