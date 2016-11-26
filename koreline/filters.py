from django_filters.rest_framework import FilterSet
from django_filters import CharFilter, NumberFilter

from koreline.models import Lesson


class LessonFilter(FilterSet):
    teacher = CharFilter(name='teacher__user__username')
    subject = CharFilter(name='subject__name')
    stage = CharFilter(name='stage__name')
    minPrice = NumberFilter(name='price', lookup_expr='gte')
    maxPrice = NumberFilter(name='price', lookup_expr='lte')

    class Meta:
        model = Lesson
        fields = ['teacher', 'slug', 'subject', 'stage', 'minPrice', 'maxPrice']
