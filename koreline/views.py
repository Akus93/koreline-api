from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from koreline.serializers import UserSerializer, UserProfileSerializer
from koreline.models import UserProfile


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        current_user = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(current_user)
        return Response(serializer.data)
