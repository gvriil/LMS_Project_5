from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from . import views
from materials.models import Course, Lesson

User = get_user_model()


class CourseViewsTestCase(APITestCase):
    """Тесты для представлений курсов."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='securepassword123'
        )
        self.course_data = {
            'title': 'Тестовый курс',
            'description': 'Описание тестового курса',
            'owner': self.user
        }
        self.course = Course.objects.create(**self.course_data)

    def test_course_list(self):
        """Тест получения списка курсов."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_detail(self):
        """Тест получения деталей курса."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.course_data['title'])

    def test_course_create(self):
        """Тест создания курса."""
        self.client.force_authenticate(user=self.user)
        new_course_data = {
            'title': 'Новый курс',
            'description': 'Описание нового курса'
        }
        response = self.client.post('/api/courses/', new_course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)


class LessonViewsTestCase(APITestCase):
    """Тесты для представлений уроков."""

    def setUp(self):
        """Настройка тестового окружения."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='securepassword123'
        )
        self.course = Course.objects.create(
            title='Тестовый курс',
            description='Описание тестового курса',
            owner=self.user
        )
        self.lesson_data = {
            'title': 'Тестовый урок',
            'description': 'Описание тестового урока',
            'course': self.course,
            'owner': self.user
        }
        self.lesson = Lesson.objects.create(**self.lesson_data)

    def test_lesson_list(self):
        """Тест получения списка уроков."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_detail(self):
        """Тест получения деталей урока."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.lesson_data['title'])

    def test_lesson_create(self):
        """Тест создания урока."""
        self.client.force_authenticate(user=self.user)
        new_lesson_data = {
            'title': 'Новый урок',
            'description': 'Описание нового урока',
            'course': self.course.id,
            'video_url': 'https://www.youtube.com/watch?v=validId'

        }
        response = self.client.post('/api/lessons/', new_lesson_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
