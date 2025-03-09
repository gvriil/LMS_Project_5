from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Payment
from .serializers import PaymentSerializer
from .serializers import UserSerializer, UserCreateSerializer

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]



class PaymentFilter(filters.FilterSet):
    class Meta:
        model = Payment
        fields = {
            'date': ['gte', 'lte'],
            'course': ['exact'],
            'lesson': ['exact'],
            'payment_method': ['exact']
        }


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    ordering_fields = ['date']
