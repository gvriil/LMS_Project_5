from django.urls import path
from .views import UserProfileView, UserRegistrationView, PaymentListView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user-profile'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
]