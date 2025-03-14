import os
from celery import Celery
from django.conf import settings

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра приложения Celery
app = Celery('lms_project')

# Загрузка настроек из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

from celery.schedules import crontab

# Предопределенные расписания задач
app.conf.beat_schedule = {
    'deactivate-inactive-users': {
        'task': 'materials.tasks.deactivate_inactive_users',
        # Запуск раз в сутки в 00:00
        'schedule': crontab(hour=0, minute=0),
    },
}