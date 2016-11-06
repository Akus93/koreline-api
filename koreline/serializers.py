from rest_framework import serializers
from django.contrib.auth.models import User

from koreline.models import UserProfile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    firstName = serializers.CharField(source='first_name', allow_blank=True)
    lastName = serializers.CharField(source='last_name', allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'firstName', 'lastName', 'email')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    birthDate = serializers.DateField(source='birth_date', allow_null=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'birthDate')

    def update(self, instance, validated_data):
        try:
            user_data = validated_data.pop('user')
        except KeyError:
            user_data = {}
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        if first_name:
            instance.user.first_name = first_name
        if last_name:
            instance.user.last_name = last_name

        if last_name or first_name:
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
