from base64 import b64decode
from uuid import uuid4

from django.core.files.base import ContentFile
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify

from koreline.models import UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification


class ImageBase64Field(serializers.ImageField):
    def to_internal_value(self, data):
        try:
            decoded_image = b64decode(data.split(',')[1])
        except TypeError:
            raise serializers.ValidationError('Niepoprawny format zdjęcia.')
        data = ContentFile(decoded_image, name=str(uuid4()) + '.png')
        return super(ImageBase64Field, self).to_internal_value(data)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    firstName = serializers.CharField(source='first_name', allow_blank=True)
    lastName = serializers.CharField(source='last_name', allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'firstName', 'lastName', 'email')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    birthDate = serializers.DateField(source='birth_date', allow_null=True)
    isTeacher = serializers.BooleanField(source='is_teacher', read_only=True)
    photo = ImageBase64Field()

    class Meta:
        model = UserProfile
        fields = ('user', 'birthDate', 'isTeacher', 'photo', 'tokens')

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


class LessonSerializer(serializers.ModelSerializer):
    teacher = UserProfileSerializer(read_only=True)
    slug = serializers.SlugField(read_only=True)
    subject = serializers.CharField(source='subject_name')
    stage = serializers.CharField(source='stage_name')

    class Meta:
        model = Lesson
        fields = ('title', 'slug', 'subject', 'stage', 'price', 'teacher')

    def create(self, validated_data):
        subject = validated_data['subject_name']
        if Subject.objects.filter(name=subject).exists():
            validated_data['subject'] = Subject.objects.get(name=subject)
            del validated_data['subject_name']
        else:
            raise serializers.ValidationError({'subject': 'Nie ma takiego przedmiotu.'})

        stage = validated_data['stage_name']
        if Stage.objects.filter(name=stage).exists():
            validated_data['stage'] = Stage.objects.get(name=stage)
            del validated_data['stage_name']
        else:
            raise serializers.ValidationError({'stage': 'Nie ma takiego poziomu.'})

        slug = slugify(validated_data['title'])
        number = 0
        while Lesson.objects.filter(slug=slug).exists():
            number += 1
            slug = slugify('{}-{}'.format(validated_data['title'], str(number)))
        validated_data['slug'] = slug
        return super(LessonSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('stage_name', None):
            del validated_data['stage_name']
        if validated_data.get('subject_name'):
            del validated_data['subject_name']

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


class LessonMembershipSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()
    student = UserProfileSerializer()

    class Meta:
        model = LessonMembership
        fields = ('lesson', 'student', 'create_date')


class RoomSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()
    student = UserProfileSerializer()

    class Meta:
        model = Room
        fields = ('lesson', 'student', 'key', 'create_date')


class NotificationSerializer(serializers.ModelSerializer):
    isRead = serializers.BooleanField(source='is_read')
    createDate = serializers.DateTimeField(source='create_date')

    class Meta:
        model = Notification
        fields = ('title', 'text', 'isRead', 'createDate')
