from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView

from materials.views import LessonListCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list'),
    path('api/', include('materials.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]