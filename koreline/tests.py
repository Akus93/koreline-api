from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from koreline.models import UserProfile, Lesson, Subject, Stage
from koreline.serializers import UserProfileSerializer, LessonSerializer


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


class SubjectsTests(BaseApiTest):

    def test_get_subjects(self):
        url = '/api/subjects/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(response.data[0], self.test_subject.name)




