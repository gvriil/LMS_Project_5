from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from materials.models import Course
from users.models import Payment

User = get_user_model()


class PaymentModelTestCase(TestCase):
    def setUp(self):
        """Настройка тестового окружения."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )

        # Создаём тестовый курс
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание тестового курса"
        )

        # Используем созданный объект курса
        self.payment_data = {
            'user': self.user,
            'date': timezone.now().date(),
            'course': self.course,  # используем объект, а не ID
            'amount': Decimal('100.00'),
            'payment_method': 'card'
        }

        self.payment = Payment.objects.create(**self.payment_data)

    def test_payment_creation(self):
        """Тест создания платежа."""
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.course, self.course)
        self.assertEqual(self.payment.amount, Decimal('100.00'))
        self.assertEqual(self.payment.payment_method, 'card')

    def test_payment_str_method(self):
        """Тест строкового представления платежа."""
        expected = f"Платеж от {self.user.email} на сумму {self.payment.amount}"
        self.assertEqual(str(self.payment), expected)


def setUp(self):
    # Создаем пользователя
    self.user = User.objects.create_user(
        email='test@example.com',
        password='testpassword',
        first_name='Test',
        last_name='User'
    )

    # Создаем тестовый курс
    from materials.models import Course
    self.course = Course.objects.create(
        title="Тестовый курс",
        description="Описание тестового курса"
    )

    # Создаем платеж с правильной ссылкой на курс
    self.payment_data = {
        'user': self.user,
        'date': timezone.now().date(),
        'course': self.course,  # объект курса вместо ID
        'amount': Decimal('100.00'),
        'payment_method': 'card'
    }
    self.payment = Payment.objects.create(**self.payment_data)
