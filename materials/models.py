from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from config import settings
from config.settings import NULLABLE


class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/', verbose_name='Превью', **NULLABLE)
    description = models.TextField(verbose_name='Описание')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              verbose_name='Владелец курса', **NULLABLE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='цена')

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка', default=0
    )
    last_notification_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=150, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    preview = models.ImageField(upload_to='lessons/', verbose_name='Превью', **NULLABLE)
    video_url = models.URLField(verbose_name='Ссылка на видео')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              verbose_name='Владелец курса', **NULLABLE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'


class CourseSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name='Пользователь', related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE,
                               verbose_name='Курс', related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.title}"


class Payment(models.Model):
    """Модель платежа"""

    PAYMENT_STATUS = (
        ('created', 'Создан'),
        ('succeeded', 'Оплачен'),
        ('canceled', 'Отменен'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='materials_payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_link = models.URLField(verbose_name="Ссылка на оплату", **NULLABLE)
    session_id = models.CharField(max_length=150, verbose_name="ID сессии Stripe", **NULLABLE)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="created",
                              verbose_name="Статус платежа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Платеж {self.id} - {self.course.title}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"