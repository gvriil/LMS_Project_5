from django.core.exceptions import ValidationError
import re


def validate_youtube_url(value):
    """
    Проверяет, что URL ссылается только на youtube.com.
    """
    if value:
        youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/'
        if not re.match(youtube_pattern, value):
            raise ValidationError(
                'Разрешены только ссылки на youtube.com'
            )
    return value