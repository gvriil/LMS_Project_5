from django.urls import path
from . import views

urlpatterns = [
    # Маршруты для курсов (используйте существующие views)
    path('courses/', views.CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),

    # Маршруты для уроков
    path('lessons/', views.LessonListCreateView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),

    # Платежные маршруты (сохраняем)
    path('payment/create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('payment/check-status/', views.PaymentStatusView.as_view(), name='payment-check-status'),
    path('payment/', views.PaymentListView.as_view(), name='payment-list'),
]