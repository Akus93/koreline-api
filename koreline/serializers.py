from base64 import b64decode
from uuid import uuid4

from django.core.files.base import ContentFile
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify

from koreline.models import UserProfile, Lesson, Subject, Stage, LessonMembership, Room, Notification, Message,\
                            Comment, ReportedComment, Bill


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
        fields = ('user', 'birthDate', 'isTeacher', 'photo', 'tokens', 'headline', 'biography')

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
    shortDescription = serializers.CharField(source='short_description')
    longDescription = serializers.CharField(source='long_description')

    class Meta:
        model = Lesson
        fields = ('title', 'slug', 'subject', 'stage', 'price', 'teacher', 'shortDescription', 'longDescription')

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
        fields = ('id', 'title', 'text', 'isRead', 'createDate', 'type', 'data')


class MessageSerializer(serializers.ModelSerializer):
    isRead = serializers.BooleanField(source='is_read', required=False)
    createDate = serializers.DateTimeField(source='create_date', required=False)
    sender = UserProfileSerializer(read_only=True)
    reciver = UserProfileSerializer(read_only=True)

    sender_save = serializers.CharField(write_only=True)
    reciver_save = serializers.CharField(write_only=True)

    class Meta:
        model = Message
        fields = ('id', 'sender', 'reciver', 'title', 'text', 'isRead', 'createDate', 'sender_save', 'reciver_save')

    def create(self, validated_data):
        reciver_username = validated_data.pop('reciver_save', None)
        sender_username = validated_data.pop('sender_save', None)

        try:
            reciver = UserProfile.objects.get(user__username=reciver_username)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({'reciver': 'Nie ma takiego użytkownika.'})

        sender = UserProfile.objects.get(user__username=sender_username)

        if reciver.id == sender.id:
            raise serializers.ValidationError({'reciver': 'Nie można wysłać wiadomości do siebie.'})

        validated_data['reciver'] = reciver
        validated_data['sender'] = sender

        return super(MessageSerializer, self).create(validated_data)


class LastMessageSerializer(serializers.Serializer):
    user = UserProfileSerializer(read_only=True)
    message = MessageSerializer(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CommentSerizalizer(serializers.ModelSerializer):
    createDate = serializers.DateTimeField(source='create_date', read_only=True)
    author = UserProfileSerializer(read_only=True)
    teacher = UserProfileSerializer(read_only=True)

    author_save = serializers.CharField(write_only=True)
    teacher_save = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'teacher', 'text', 'rate', 'createDate', 'author_save', 'teacher_save')

    def create(self, validated_data):
        author_username = validated_data.pop('author_save', None)
        teacher_username = validated_data.pop('teacher_save', None)

        try:
            teacher = UserProfile.objects.get(user__username=teacher_username)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({'teacher': 'Nie ma takiego użytkownika.'})

        author = UserProfile.objects.get(user__username=author_username)

        if teacher.id == author.id:
            raise serializers.ValidationError({'teacher': 'Nie można oceniać swojego profilu.'})

        validated_data['author'] = author
        validated_data['teacher'] = teacher

        return super(CommentSerizalizer, self).create(validated_data)


class ReportedCommentSerizalizer(serializers.ModelSerializer):
    createDate = serializers.DateTimeField(source='create_date', read_only=True)
    author = UserProfileSerializer(read_only=True)
    comment = CommentSerizalizer(read_only=True)

    author_save = serializers.CharField(write_only=True)
    comment_save = serializers.CharField(write_only=True)

    class Meta:
        model = ReportedComment
        fields = ('author', 'comment', 'text', 'createDate', 'author_save', 'comment_save')

    def create(self, validated_data):
        author_username = validated_data.pop('author_save', None)
        comment_id = validated_data.pop('comment_save', None)

        try:
            comment = Comment.objects.get(id=comment_id, is_active=True)
        except Comment.DoesNotExist:
            raise serializers.ValidationError({'comment': 'Nie ma takiego komentarza.'})

        author = UserProfile.objects.get(user__username=author_username)

        if ReportedComment.objects.filter(comment=comment, author=author).count():
            raise serializers.ValidationError({'comment': 'Już zgłosiłeś/aś ten komentarz.'})

        validated_data['author'] = author
        validated_data['comment'] = comment

        return super(ReportedCommentSerizalizer, self).create(validated_data)


class BillSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    lesson = LessonSerializer()
    createDate = serializers.DateTimeField(source='create_date', read_only=True)
    paidDate = serializers.DateTimeField(source='paid_date', read_only=True, allow_null=True)
    isPaid = serializers.BooleanField(source='is_paid', read_only=True)

    class Meta:
        model = Bill
        fields = ('id', 'user', 'lesson', 'amount', 'isPaid', 'paidDate', 'createDate')
