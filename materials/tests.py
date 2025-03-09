from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Course, Lesson, CourseSubscription

User = get_user_model()

class MaterialsAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            password='testpassword',
            email='testuser@example.com'
        )
        self.moderator = User.objects.create_user(
            password='modpassword',
            email='moderator@example.com',
            is_staff=True
        )
        self.course = Course.objects.create(title='Test Course', owner=self.user)
        self.lesson = Lesson.objects.create(title='Test Lesson', course=self.course, owner=self.user)

    def test_create_lesson(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/lessons/create/'
        data = {
            'title': 'New Lesson',
            'course': self.course.id,
            'description': 'Test description',
            'video_url': 'https://youtube.com/watch?v=dQw4w9WgXcQ'
            # Используйте реальный YouTube URL
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_lesson(self):
        self.client.force_authenticate(user=self.user)
        url = f'/api/lessons/{self.lesson.id}/update/'
        data = {
            'title': 'Updated Lesson',
            'course': self.course.id,
            'description': 'Updated description',
            'video_url': 'https://youtube.com/watch?v=dQw4w9WgXcQ'
            # Используйте реальный YouTube URL
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_access_by_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        # Сначала создаем урок от имени модератора
        new_lesson = Lesson.objects.create(
            title='Mod Lesson',
            course=self.course,
            owner=self.moderator,
            description='Moderator test',
            video_url='https://youtube.com/watch?v=dQw4w9WgXcQ'
        )
        url = f'/api/lessons/{new_lesson.id}/update/'
        data = {
            'title': 'Moderator Updated Own Lesson',
            'course': self.course.id,
            'description': 'Moderator update',
            'video_url': 'https://youtube.com/watch?v=dQw4w9WgXcQ'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lesson(self):
        self.client.force_authenticate(user=self.user)
        url = f'/api/lessons/{self.lesson.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_subscription(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/subscription/'
        response = self.client.post(url, {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_lesson_access_by_anonymous(self):
        url = f'/api/lessons/{self.lesson.id}/'
        response = self.client.get(url)
        # Исправьте ожидаемый код
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)