from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify

from koreline.models import UserProfile, Lesson, Subject


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


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ('name',)


class LessonSerializer(serializers.ModelSerializer):
    teacher = UserProfileSerializer(read_only=True)
    slug = serializers.SlugField(read_only=True)
    subject = serializers.CharField(source='subject_name')

    class Meta:
        model = Lesson
        fields = ('title', 'slug', 'subject', 'price', 'teacher')

    def create(self, validated_data):
        subject = validated_data['subject_name']
        if Subject.objects.filter(name=subject).exists():
            validated_data['subject'] = Subject.objects.get(name=subject)
            del validated_data['subject_name']
        else:
            raise serializers.ValidationError({'subject': 'Nie ma takiego przedmiotu.'})
        slug = slugify(validated_data['title'])
        number = 0
        while Lesson.objects.filter(slug=slug).exists():
            number += 1
            slug = slugify('{}-{}'.format(validated_data['title'], str(number)))
        validated_data['slug'] = slug
        return super(LessonSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        title = validated_data.get('title', None)
        if title:
            slug = slugify(title)
            number = 0
            while Lesson.objects.filter(slug=slug).exists():
                number += 1
                slug = slugify('{}-{}'.format(title, str(number)))
            validated_data['slug'] = slug
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
