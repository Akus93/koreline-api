from rest_framework.viewsets import ModelViewSet

from koreline.permissions import IsOwnerOrReadOnly
from koreline.serializers import UserProfileSerializer
from koreline.models import UserProfile


class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ['get', 'patch', 'head', 'delete']

