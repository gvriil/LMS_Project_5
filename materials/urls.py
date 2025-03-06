from django.urls import path, include
from .views import CourseViewSet, LessonCreateView, LessonDetailView, LessonUpdateView, LessonDeleteView
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson-create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/update/', LessonUpdateView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson-delete'),
    path('subscription/', CourseSubscriptionView.as_view(), name='course-subscription'),
                ]