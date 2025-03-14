from celery import shared_task


@shared_task
def example_task():
    """Пример периодической задачи для демонстрации работы Celery."""
    print(f"Example task executed at {datetime.now()}")
    return "Task completed successfully"


from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


@shared_task
def send_course_update_notification(course_id, course_title):
    """Отправляет уведомление подписчикам о обновлении курса."""
    from .models import CourseSubscription

    # Получаем всех подписчиков курса
    subscriptions = CourseSubscription.objects.filter(course_id=course_id)

    for subscription in subscriptions:
        user = subscription.user

        subject = f'Обновление в курсе "{course_title}"'
        message = f'Здравствуйте, {user.username}!\n\nВ курсе "{course_title}", на который вы подписаны, появилось обновление.\n\nС уважением,\nКоманда LMS'

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    return f"Отправлены уведомления {subscriptions.count()} подписчикам курса {course_title}"


from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не входили в систему более месяца.
    """
    User = get_user_model()
    # Вычисляем дату месяц назад от текущей
    month_ago = timezone.now() - timedelta(days=30)

    # Находим пользователей с датой входа старше месяца или с пустым значением last_login,
    # но созданных более месяца назад, которые активны
    inactive_users = User.objects.filter(
        is_active=True
    ).filter(
        last_login__lt=month_ago
    ) | User.objects.filter(
        is_active=True,
        last_login__isnull=True,
        date_joined__lt=month_ago
    )

    # Деактивируем найденных пользователей
    count = inactive_users.count()
    inactive_users.update(is_active=False)

    return f"Деактивировано {count} неактивных пользователей"
