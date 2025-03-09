from django.urls import path, include
from .views import (
    CourseViewSet, LessonDetailView, LessonUpdateView,
    LessonDeleteView, CourseSubscriptionView, LessonListCreateView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/update/', LessonUpdateView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson-delete'),
    path('course/subscription/', CourseSubscriptionView.as_view(), name='course-subscription'),
]

urlpatterns += router.urls