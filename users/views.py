from rest_framework import generics
from django_filters import rest_framework as filters
from .models import Payment
from .serializers import PaymentSerializer

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