from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from koreline.models import UserProfile, Lesson, Subject, Stage, Message, LessonMembership, Room, Comment, \
                            ReportedComment, Notification, AccountOperation, Bill
from koreline.serializers import UserProfileSerializer, LessonSerializer, MessageSerializer, RoomSerializer,\
                                 CommentSerizalizer, ReportedCommentSerizalizer, NotificationSerializer


class BaseApiTest(APITestCase):

    def setUp(self):
        test_student_user = User.objects.create_user(username='student', email='student@test.com',
                                                     password='student123password', first_name='Jan',
                                                     last_name='Kowalski')
        self.test_student = UserProfile.objects.get(user=test_student_user)
        self.test_student_token = Token.objects.create(user=test_student_user, key='RANDOMstudentTOKEN')

        test_teacher_user = User.objects.create_user(username='teacher', email='teacher@test.com',
                                                     password='teacher123password', first_name='Anna',
                                                     last_name='Nowak')
        self.test_teacher_token = Token.objects.create(user=test_teacher_user, key='RANDOMteacherTOKEN')
        test_teacher = UserProfile.objects.get(user=test_teacher_user)
        test_teacher.is_teacher = True
        test_teacher.save()
        self.test_teacher = test_teacher
        self.test_subject = Subject.objects.create(name='Test subject')
        self.test_stage = Stage.objects.create(name='Test stage')
        self.test_lesson = Lesson.objects.create(teacher=self.test_teacher, title='Test title',
                                                 subject=self.test_subject, short_description='Test short description',
                                                 slug='test-title', price=20, long_description='Test long desctiption',
                                                 stage=self.test_stage)


class RegistrationTests(BaseApiTest):

    def test_success_registration(self):
        url = '/auth/registration/'
        data = {'email': 'dawid.rdzanek@gmail.com', 'password1': 'testpassword123', 'password2': 'testpassword123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(UserProfile.objects.count(), 3)
        self.assertEqual(UserProfile.objects.last().user.username, 'dawid.rdzanek')
        self.assertEqual(UserProfile.objects.last().user.email, 'dawid.rdzanek@gmail.com')
        self.assertEqual(Token.objects.filter(user__username='dawid.rdzanek').count(), 1)
        self.assertEqual(response.data, {'key': Token.objects.get(user__username='dawid.rdzanek').key})

    def test_success_registration_add_number_if_username_exist(self):
        url = '/auth/registration/'
        data = {'email': 'student@otherdomain.com', 'password1': 'testpassword123', 'password2': 'testpassword123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email='student@otherdomain.com').username, 'student2')

    def test_unsuccess_registration_existing_email(self):
        url = '/auth/registration/'
        data = {'email': 'student@test.com', 'password1': 'testpassword123', 'password2': 'testpassword123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('email' in response.data)

    def test_unsuccess_registration_different_passwords(self):
        url = '/auth/registration/'
        data = {'email': 'other.test@student.com', 'password1': 'testpassword123', 'password2': 'differentpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'non_field_errors': ['Hasła się nie zgadzają.']})

    def test_unsuccess_registration_wrong_email_format(self):
        url = '/auth/registration/'
        data = {'email': 'teststudent.c', 'password1': 'testpassword123', 'password2': 'testpassword123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(BaseApiTest):

    def test_success_login(self):
        url = '/auth/login/'
        data = {'email': 'student@test.com', 'password': 'student123password'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'key': Token.objects.get(user__username='student').key})

    def test_unsuccess_login_wrong_credentials(self):
        url = '/auth/login/'
        data = {'email': 'wrong@test.com', 'password': 'wrongpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTests(BaseApiTest):

    def test_get_userprofile(self):
        url = '/api/users/' + self.test_teacher.user.username + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, UserProfileSerializer(self.test_teacher).data)
        self.assertEqual(response.data['user']['username'], self.test_teacher.user.username)

    def test_success_patch_userprofile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/users/' + self.test_teacher.user.username + '/'
        data = {
            'user': {'firstName': 'Adam'},
            'headline': 'Test headline'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfile.objects.get(pk=self.test_teacher.id).user.first_name, data['user']['firstName'])
        self.assertEqual(UserProfile.objects.get(pk=self.test_teacher.id).headline, data['headline'])
        self.client.credentials()

    def test_unsuccess_patch_userprofile_by_non_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/users/' + self.test_teacher.user.username + '/'
        old_first_name = self.test_teacher.user.first_name
        old_headline = self.test_teacher.headline
        data = {
            'user': {'firstName': 'Adam'},
            'headline': 'Test headline'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(UserProfile.objects.get(pk=self.test_teacher.id).user.first_name, old_first_name)
        self.assertEqual(UserProfile.objects.get(pk=self.test_teacher.id).headline, old_headline)
        self.client.credentials()

    def test_success_get_own_userprofile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/user/my-profile/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, UserProfileSerializer(self.test_teacher).data)
        self.client.credentials()

    def test_unsuccess_get_own_userprofile_by_unauth(self):
        self.client.credentials()
        url = '/api/user/my-profile/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LessonTests(BaseApiTest):

    def test_get_lessons(self):
        url = '/api/lessons/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], LessonSerializer(Lesson.objects.first()).data)

    def test_success_create_lesson(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/lessons/'
        data = {
            'title': 'Title for test_create_lesson',
            'subject': 'Test subject',
            'stage': 'Test stage',
            'price': 50,
            'shortDescription': 'Short desc for test_create_lesson',
            'longDescription': 'Long desc for test_create_lesson'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, LessonSerializer(Lesson.objects.first()).data)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.first().slug, slugify(data['title']))
        self.client.credentials()

    def test__create_lesson_student_become_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/lessons/'
        data = {
            'title': 'Title for test_create_lesson',
            'subject': 'Test subject',
            'stage': 'Test stage',
            'price': 50,
            'shortDescription': 'Short desc for test_create_lesson',
            'longDescription': 'Long desc for test_create_lesson'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserProfile.objects.get(user__username='student').is_teacher, True)
        self.client.credentials()

    def test_success_patch_lesson(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/lessons/' + slugify(self.test_lesson.title) + '/'
        data = {
            'title': 'Changed title',
            'shortDescription': 'Changed short desc',
            'longDescription': 'Changed long desc'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Lesson.objects.first().title, data['title'])
        self.assertEqual(Lesson.objects.first().short_description, data['shortDescription'])
        self.assertEqual(Lesson.objects.first().long_description, data['longDescription'])
        self.client.credentials()

    def test_unsuccess_patch_lesson_by_nonauthor(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/lessons/' + slugify(self.test_lesson.title) + '/'
        data = {
            'title': 'Changed title',
            'shortDescription': 'Changed short desc',
            'longDescription': 'Changed long desc'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(Lesson.objects.first().title, data['title'])
        self.assertNotEqual(Lesson.objects.first().short_description, data['shortDescription'])
        self.assertNotEqual(Lesson.objects.first().long_description, data['longDescription'])
        self.client.credentials()

    def test_unsuccess_patch_lesson_unallowed_field_slug(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/lessons/' + slugify(self.test_lesson.title) + '/'
        old_slug = self.test_lesson.slug
        data = {
            'slug': 'new_slug',
        }
        self.client.patch(url, data)
        self.assertEqual(Lesson.objects.get(pk=self.test_lesson.id).slug, old_slug)
        self.client.credentials()

    def test_success_delete_lesson(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/lessons/' + slugify(self.test_lesson.title) + '/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_delete_lesson_by_nonauthor(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/lessons/' + slugify(self.test_lesson.title) + '/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)
        self.client.credentials()


class StageTests(BaseApiTest):

    def test_get_stages(self):
        url = '/api/stages/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(response.data[0], self.test_stage.name)


class SubjectTests(BaseApiTest):

    def test_get_subjects(self):
        url = '/api/subjects/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(response.data[0], self.test_subject.name)


class MessageTests(BaseApiTest):

    def setUp(self):
        super(MessageTests, self).setUp()
        self.test_message = Message.objects.create(reciver=self.test_student, sender=self.test_teacher,
                                                   title='Test title', text='Test text')

    def test_success_send_message(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/messages/'
        data = {
            'reciver': 'teacher',
            'title': 'Test message title',
            'text': 'Test message text',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(response.data, MessageSerializer(Message.objects.first()).data)
        self.assertEqual(response.data['isRead'], False)
        self.assertEqual(Message.objects.first().reciver.user.username, self.test_teacher.user.username)
        self.client.credentials()

    def test_unsuccess_send_message_unauthorized(self):
        url = '/api/messages/'
        data = {
            'reciver': 'teacher',
            'title': 'Test message title',
            'text': 'Test message text',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Message.objects.count(), 1)

    def test_unsuccess_send_message_to_self(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/messages/'
        data = {
            'reciver': 'student',
            'title': 'Test message title',
            'text': 'Test message text',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('reciver' in response.data)
        self.assertEqual(Message.objects.count(), 1)
        self.client.credentials()

    def test_success_get_interlocutors(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/messages/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], UserProfileSerializer(self.test_teacher).data)
        self.client.credentials()

    def test_success_mark_as_read(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/messages/'
        response = self.client.put(url, {'id': self.test_message.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['isRead'], True)
        self.assertEqual(Message.objects.first().is_read, True)
        self.client.credentials()

    def test_unsuccess_mark_as_read_by_non_reciver(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/messages/'
        response = self.client.put(url, {'id': self.test_message.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Message.objects.first().is_read, False)
        self.client.credentials()

    def test_success_get_unread_messages(self):
        Message.objects.create(reciver=self.test_student, sender=self.test_teacher, title='Title', text='Text',
                               is_read=True)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/messages/unread/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, MessageSerializer(Message.objects.filter(reciver__user__username='student',
                                                                                 is_read=False), many=True).data)
        self.client.credentials()

    def test_success_get_messages_with_user(self):
        Message.objects.create(reciver=self.test_teacher, sender=self.test_student, title='Title', text='Text')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/messages/{}/'.format(self.test_teacher.user.username)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.client.credentials()

    def test_unsuccess_get_messages_with_user_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/messages/{}/'.format('none.existing')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.credentials()

    def test_unsuccess_get_messages_with_user_unauthorized(self):
        url = '/api/messages/{}/'.format('teacher')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LessonMembershipTests(BaseApiTest):

    def test_success_join_to_lesson(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/lessons/join/'
        data = {
            'lesson': self.test_lesson.slug,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.assertEqual(LessonMembership.objects.first().student, self.test_student)
        self.assertEqual(LessonMembership.objects.first().lesson, self.test_lesson)

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().type, 'SUBSCRIBE')
        self.assertEqual(Notification.objects.first().user, self.test_teacher)
        self.assertEqual(Notification.objects.first().data, self.test_student.user.username)

        self.client.credentials()

    def test_unsuccess_join_to_lesson_unauthorized(self):
        url = '/api/lessons/join/'
        data = {
            'lesson': self.test_lesson.slug,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(LessonMembership.objects.count(), 0)

    def test_unsuccess_join_to_lesson_rejoin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/lessons/join/'
        data = {
            'lesson': self.test_lesson.slug,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LessonMembership.objects.count(), 1)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.assertTrue('error' in response.data)
        self.client.credentials()

    def test_success_leave_lesson(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(LessonMembership.objects.count(), 1)

        url = '/api/lessons/leave/'
        data = {
            'lesson': self.test_lesson.slug,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LessonMembership.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_leave_lesson_unauthorized(self):
        LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(LessonMembership.objects.count(), 1)

        url = '/api/lessons/leave/'
        data = {
            'lesson': self.test_lesson.slug,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(LessonMembership.objects.count(), 1)

    def test_unsuccess_leave_lesson_unknow_lesson(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(LessonMembership.objects.count(), 1)

        url = '/api/lessons/leave/'
        data = {
            'lesson': 'unknow-lesson',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.client.credentials()

    def test_unsuccess_leave_lesson_not_member(self):
        new_lesson = Lesson.objects.create(teacher=self.test_teacher, title='New title', subject=self.test_subject,
                                           short_description='New short description', slug='new-test-title', price=50,
                                           long_description='New long desctiption', stage=self.test_stage)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(Lesson.objects.count(), 2)

        url = '/api/lessons/leave/'
        data = {
            'lesson': new_lesson.slug,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.client.credentials()

    def test_success_get_members_list(self):
        new_student = User.objects.create_user(username='new.student', email='new.student@test.com',
                                               password='asdjndfg')
        LessonMembership.objects.create(lesson=self.test_lesson, student=new_student.userprofile)
        LessonMembership.objects.create(lesson=self.test_lesson, student=self.test_student)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        self.assertEqual(LessonMembership.objects.count(), 2)

        url = '/api/lessons/' + self.test_lesson.slug + '/members/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0], UserProfileSerializer(self.test_student).data)
        self.client.credentials()

    def test_unsuccess_get_members_list_unauthorized(self):
        new_student = User.objects.create_user(username='new.student', email='new.student@test.com',
                                               password='asdjndfg')
        LessonMembership.objects.create(lesson=self.test_lesson, student=new_student.userprofile)
        LessonMembership.objects.create(lesson=self.test_lesson, student=self.test_student)

        self.assertEqual(LessonMembership.objects.count(), 2)

        url = '/api/lessons/' + self.test_lesson.slug + '/members/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unsuccess_get_members_list_not_lesson_owner(self):
        new_student = User.objects.create_user(username='new.student', email='new.student@test.com',
                                               password='asdjndfg')
        LessonMembership.objects.create(lesson=self.test_lesson, student=new_student.userprofile)
        LessonMembership.objects.create(lesson=self.test_lesson, student=self.test_student)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        self.assertEqual(LessonMembership.objects.count(), 2)

        url = '/api/lessons/' + self.test_lesson.slug + '/members/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials()

    def test_unsuccess_get_members_list_unknown_lesson(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)

        url = '/api/lessons/' + 'unknown' + '/members/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.credentials()

    def test_success_get_members_empty(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        self.assertEqual(LessonMembership.objects.count(), 0)
        url = '/api/lessons/' + self.test_lesson.slug + '/members/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.credentials()

    def test_success_unsubscribe_student_from_lesson(self):
        membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/lessons/unsubscribe/'
        data = {
            'lesson': membership.lesson.slug,
            'username': membership.student.user.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LessonMembership.objects.count(), 0)

        self.assertEqual(Notification.objects.count(), 3)
        self.assertTrue(Notification.objects.filter(user=self.test_student, type='STUDENT_UNSUBSCRIBE').exists())
        self.assertTrue(Notification.objects.filter(user=self.test_teacher, type='TEACHER_UNSUBSCRIBE').exists())

        self.client.credentials()

    def test_unsuccess_unsubscribe_student_from_lesson_unknown_student(self):
        membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/lessons/unsubscribe/'
        data = {
            'lesson': membership.lesson.slug,
            'username': 'unknown'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.client.credentials()

    def test_unsuccess_unsubscribe_student_from_lesson_unknown_lesson(self):
        membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/lessons/unsubscribe/'
        data = {
            'lesson': 'unknown',
            'username': membership.student.user.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.client.credentials()

    def test_success_get_student_lessons(self):
        membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(LessonMembership.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/user/my-lessons/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(response.data[0], LessonSerializer(membership.lesson).data)
        self.client.credentials()

    def test_unsuccess_get_student_lessons_unauthorized(self):
        LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.assertEqual(LessonMembership.objects.count(), 1)
        url = '/api/user/my-lessons/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RoomTests(BaseApiTest):

    def setUp(self):
        super(RoomTests, self).setUp()
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)

    def test_success_open_room(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/room/open/'
        data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(Room.objects.first().is_open, True)
        self.assertEqual(response.data, RoomSerializer(Room.objects.first()).data)

        notifications = Notification.objects.filter(user=self.test_student)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].type, 'INVITE')
        self.assertEqual(notifications[0].is_read, False)
        self.client.credentials()

    def test_unsuccess_open_room_unknown_lesson(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/room/open/'
        data = {
            'lesson': 'unknown',
            'student': self.test_membership.student.user.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Room.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_open_room_unknown_student(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/room/open/'
        data = {
            'lesson': self.test_membership.lesson.slug,
            'student': 'unknown'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Room.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_open_room_student_not_member(self):
        new_student = User.objects.create_user(username='new.student', email='new.student@test.com',
                                               password='asdjndfg')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/room/open/'
        data = {
            'lesson': self.test_membership.lesson.slug,
            'student': new_student.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Room.objects.count(), 0)
        self.client.credentials()

    def test_success_close_room(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)

        open_url = '/api/room/open/'
        open_data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        open_response = self.client.post(open_url, open_data)
        self.assertEqual(open_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)

        url = '/api/room/close/'
        data = {
            'student': self.test_membership.student.user.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(Room.objects.first().is_open, False)
        self.client.credentials()

    def test_unsuccess_close_room_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        open_url = '/api/room/open/'
        open_data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        open_response = self.client.post(open_url, open_data)
        self.assertEqual(open_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)
        self.client.credentials()

        url = '/api/room/close/'
        data = {
            'student': self.test_membership.student.user.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(Room.objects.first().is_open, True)
        self.client.credentials()

    def test_unsuccess_close_room_not_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        open_url = '/api/room/open/'
        open_data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        open_response = self.client.post(open_url, open_data)
        self.assertEqual(open_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)

        url = '/api/room/close/'
        data = {
            'student': self.test_membership.student.user.username
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(Room.objects.first().is_open, True)
        self.client.credentials()

    def test_success_get_room_fom_lesson_by_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        open_url = '/api/room/open/'
        open_data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        open_response = self.client.post(open_url, open_data)
        self.assertEqual(open_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)

        url = '/api/room/lesson/' + self.test_membership.lesson.slug + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, RoomSerializer(Room.objects.first()).data)
        self.client.credentials()

    def test_success_get_room_fom_lesson_by_student(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        open_url = '/api/room/open/'
        open_data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        open_response = self.client.post(open_url, open_data)
        self.assertEqual(open_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/room/lesson/' + self.test_membership.lesson.slug + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, RoomSerializer(Room.objects.first()).data)
        self.client.credentials()

    def test_success_get_room_fom_lesson_no_room(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/room/lesson/' + self.test_membership.lesson.slug + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.credentials()

    def test_success_get_conversation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        open_url = '/api/room/open/'
        open_data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        open_response = self.client.post(open_url, open_data)
        self.assertEqual(open_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/room/' + Room.objects.first().key + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, RoomSerializer(Room.objects.first()).data)
        self.client.credentials()

    def test_unsuccess_get_conversation_unauthorized(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        open_url = '/api/room/open/'
        open_data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        open_response = self.client.post(open_url, open_data)
        self.assertEqual(open_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)

        self.client.credentials()
        url = '/api/room/' + Room.objects.first().key + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unsuccess_get_conversation_non_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/room/' + 'unknown' + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.credentials()

    def test_unsuccess_get_conversation_not_teacher_and_not_student(self):
        new_student = User.objects.create_user(username='new.student', email='new.student@test.com',
                                               password='asdjndfg')
        new_student_token = Token.objects.create(user=new_student, key='RANDOMnewstudentTOKEN')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        open_url = '/api/room/open/'
        open_data = {
            'lesson': self.test_membership.lesson.slug,
            'student': self.test_membership.student.user.username
        }
        open_response = self.client.post(open_url, open_data)
        self.assertEqual(open_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Room.objects.count(), 1)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + new_student_token.key)
        url = '/api/room/' + Room.objects.first().key + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials()


class CommentTests(BaseApiTest):

    def test_success_create_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/comments/create/'
        data = {
            'teacher': self.test_teacher.user.username,
            'text': 'Test comment',
            'rate': 4
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data, CommentSerizalizer(Comment.objects.first()).data)

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().type, 'COMMENT')
        self.assertEqual(Notification.objects.first().user, self.test_teacher)

        self.client.credentials()

    def test_unsuccess_create_comment_unauthorized(self):
        url = '/api/comments/create/'
        data = {
            'teacher': self.test_teacher.user.username,
            'text': 'Test comment',
            'rate': 4
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 0)

    def test_unsuccess_create_comment_to_self(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/comments/create/'
        data = {
            'teacher': self.test_teacher.user.username,
            'text': 'Test comment',
            'rate': 4
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertTrue('teacher' in response.data)
        self.client.credentials()

    def test_success_get_comments_about_teacher(self):
        Comment.objects.create(author=self.test_student, teacher=self.test_teacher, text='Test text', rate=4)
        self.assertEqual(Comment.objects.count(), 1)
        url = '/api/comments/' + self.test_teacher.user.username + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(response.data, CommentSerizalizer(Comment.objects.filter(teacher=self.test_teacher),
                                                           many=True).data)

    def test_unsuccess_get_comments_about_teacher_unknown(self):
        Comment.objects.create(author=self.test_student, teacher=self.test_teacher, text='Test text', rate=4)
        self.assertEqual(Comment.objects.count(), 1)
        url = '/api/comments/' + 'unknown' + '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_success_report_comment(self):
        comment = Comment.objects.create(author=self.test_student, teacher=self.test_teacher, text='Test text', rate=4)
        self.assertEqual(Comment.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/comments/report/'
        data = {
            'comment': comment.id,
            'text': 'Test report comment',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReportedComment.objects.count(), 1)
        self.assertTrue(response.data, ReportedCommentSerizalizer(ReportedComment.objects.first()).data)
        self.assertEqual(ReportedComment.objects.first().is_pending, True)
        self.client.credentials()

    def test_unsuccess_report_comment_unauthorized(self):
        comment = Comment.objects.create(author=self.test_student, teacher=self.test_teacher, text='Test text', rate=4)
        self.assertEqual(Comment.objects.count(), 1)
        url = '/api/comments/report/'
        data = {
            'comment': comment.id,
            'text': 'Test report comment',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ReportedComment.objects.count(), 0)

    def test_unsuccess_report_comment_multiple(self):
        test_comment = Comment.objects.create(author=self.test_student, teacher=self.test_teacher, text='Text', rate=4)
        self.assertEqual(Comment.objects.count(), 1)
        ReportedComment.objects.create(author=self.test_teacher, comment=test_comment, text='Test')
        self.assertEqual(ReportedComment.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/comments/report/'
        data = {
            'comment': test_comment.id,
            'text': 'Test report comment',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('comment' in response.data)
        self.client.credentials()


class NotificationTests(BaseApiTest):

    def setUp(self):
        super(NotificationTests, self).setUp()
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)

    def test_success_get_last_unread_notifications(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/notifications/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(response.data[0]['type'], 'SUBSCRIBE')
        self.assertEqual(response.data[0]['isRead'], False)
        self.client.credentials()

    def test_unsuccess_get_last_unread_notifications_unauthorized(self):
        url = '/api/notifications/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_mark_notification_as_read(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/notifications/'
        response = self.client.put(url, {'id': Notification.objects.first().id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data, NotificationSerializer(Notification.objects.first()).data)
        self.assertEqual(response.data['isRead'], True)
        self.assertEqual(Notification.objects.first().is_read, True)
        self.client.credentials()

    def test_unsuccess_mark_notification_as_read_unknow(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/notifications/'
        response = self.client.put(url, {'id': 42})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.credentials()


class AccountOperationTests(BaseApiTest):

    def test_success_buy_tokens(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/user/tokens/buy/'
        response = self.client.post(url, {'amount': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfile.objects.get(id=self.test_teacher.id).tokens, 10)
        self.assertEqual(AccountOperation.objects.count(), 1)
        account_operation = AccountOperation.objects.first()
        self.assertEqual(account_operation.type, 'BUY')
        self.assertEqual(account_operation.user, self.test_teacher)
        self.assertEqual(account_operation.amount, 10)
        self.client.credentials()

    def test_unsuccess_buy_tokens_amount_not_int(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/user/tokens/buy/'
        response = self.client.post(url, {'amount': 'bad'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserProfile.objects.get(id=self.test_teacher.id).tokens, 0)
        self.assertEqual(AccountOperation.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_buy_tokens_bad_amount(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/user/tokens/buy/'
        response = self.client.post(url, {'amount': -20})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserProfile.objects.get(id=self.test_teacher.id).tokens, 0)
        self.assertEqual(AccountOperation.objects.count(), 0)
        self.client.credentials()

    def test_success_sell_tokens(self):
        self.test_teacher.tokens = 100
        self.test_teacher.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/user/tokens/sell/'
        response = self.client.post(url, {'amount': 20})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserProfile.objects.get(id=self.test_teacher.id).tokens, 80)
        self.assertEqual(AccountOperation.objects.count(), 1)
        account_operation = AccountOperation.objects.first()
        self.assertEqual(account_operation.type, 'SELL')
        self.assertEqual(account_operation.user, self.test_teacher)
        self.assertEqual(account_operation.amount, 20)
        self.client.credentials()

    def test_unsuccess_sell_tokens_amount_not_int(self):
        self.test_teacher.tokens = 100
        self.test_teacher.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/user/tokens/sell/'
        response = self.client.post(url, {'amount': 'bad'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserProfile.objects.get(id=self.test_teacher.id).tokens, 100)
        self.assertEqual(AccountOperation.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_sell_tokens_amount_too_much(self):
        self.test_teacher.tokens = 100
        self.test_teacher.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/user/tokens/sell/'
        response = self.client.post(url, {'amount': 120})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserProfile.objects.get(id=self.test_teacher.id).tokens, 100)
        self.assertEqual(AccountOperation.objects.count(), 0)
        self.client.credentials()


class BillTests(BaseApiTest):

    def test_success_create_bill(self):
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/bills/'
        data = {
            'lesson': self.test_lesson.slug,
            'student': self.test_student.user.username,
            'amount': 20
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bill.objects.count(), 1)
        bill = Bill.objects.first()
        self.assertEqual(bill.lesson, self.test_lesson)
        self.assertEqual(bill.user, self.test_student)
        self.assertEqual(bill.amount, 20)
        self.client.credentials()

    def test_unsuccess_create_bill_unauthorized(self):
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        url = '/api/teacher/bills/'
        data = {
            'lesson': self.test_lesson.slug,
            'student': self.test_student.user.username,
            'amount': 20
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Bill.objects.count(), 0)

    def test_unsuccess_create_bill_unknown_student(self):
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/bills/'
        data = {
            'lesson': self.test_lesson.slug,
            'student': 'unknown',
            'amount': 20
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Bill.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_create_bill_unknown_lesson(self):
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/bills/'
        data = {
            'lesson': 'unknown',
            'student': self.test_student.user.username,
            'amount': 20
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Bill.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_create_bill_student_not_member(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/bills/'
        data = {
            'lesson': self.test_lesson.slug,
            'student': self.test_student.user.username,
            'amount': 20
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Bill.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_create_bill_bad_amount(self):
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/bills/'
        data = {
            'lesson': self.test_lesson.slug,
            'student': self.test_student.user.username,
            'amount': 'bad'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Bill.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_create_bill_too_low_amount(self):
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_teacher_token.key)
        url = '/api/teacher/bills/'
        data = {
            'lesson': self.test_lesson.slug,
            'student': self.test_student.user.username,
            'amount': -20
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Bill.objects.count(), 0)
        self.client.credentials()

    def test_unsuccess_create_bill_not_lesson_owner(self):
        self.test_membership = LessonMembership.objects.create(student=self.test_student, lesson=self.test_lesson)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.test_student_token.key)
        url = '/api/teacher/bills/'
        data = {
            'lesson': self.test_lesson.slug,
            'student': self.test_teacher.user.username,
            'amount': 20
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Bill.objects.count(), 0)
        self.client.credentials()

