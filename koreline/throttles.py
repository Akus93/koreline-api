from rest_framework.throttling import UserRateThrottle


class LessonThrottle(UserRateThrottle):

    rate = '4/h'
    scope = 'lesson'

    def allow_request(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return super(LessonThrottle, self).allow_request(request, view)
