from rest_framework import serializers
from django.contrib.auth.models import User

from koreline.models import UserProfile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')

    class Meta:
        model = User
        fields = ('username', 'firstName', 'lastName', 'email')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    birthDate = serializers.DateField(source='birth_date')

    class Meta:
        model = UserProfile
        fields = ('user', 'birthDate')
