import datetime
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, CourseSubscription
from .models import Lesson
from .models import Payment
from .paginators import MaterialsPagination
from .permissions import IsModerator, IsOwner, NotModerator, ModeratorOrOwner
from .serializers import CourseSerializer, LessonSerializer
from .services import create_stripe_product, create_stripe_price, create_stripe_session, \
    get_session_status
from .services import retrieve_stripe_session
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPagination

    def get_permissions(self):
        """Определяет права доступа для разных действий."""
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), NotModerator()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), ModeratorOrOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer) -> None:
        """Сохраняет владельца при создании курса."""
        serializer.save(owner=self.request.user)


class LessonDetailView(generics.RetrieveAPIView):
    """Контроллер для просмотра урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class LessonUpdateView(generics.UpdateAPIView):
    """Контроллер для обновления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsModerator]
    pagination_class = MaterialsPagination

    def perform_update(self, serializer):
        lesson = serializer.save()

        # Получаем связанный курс
        course = lesson.course
        four_hours_ago = timezone.now() - timedelta(hours=4)

        # Проверка времени последнего уведомления
        if not course.last_notification_sent or course.last_notification_sent < four_hours_ago:
            course.last_notification_sent = timezone.now()
            course.save(update_fields=['last_notification_sent'])

            # Запускаем асинхронную рассылку
            send_course_update_notification.delay(course.id, course.title)


class LessonDeleteView(generics.DestroyAPIView):
    """Контроллер для удаления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class CourseSubscriptionView(APIView):
    """Управление подпиской на курс"""

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "Не указан ID курса"}, status=400)

        course_item = get_object_or_404(Course, pk=course_id)
        subs_item = CourseSubscription.objects.filter(user=user, course=course_item)

        # Если подписка есть - удаляем
        if subs_item.exists():
            subs_item.delete()
            message = 'подписка удалена'
        # Если подписки нет - создаем
        else:
            CourseSubscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        return Response({"message": message})


# В файле views.py добавьте:

class LessonListCreateView(generics.ListCreateAPIView):
    @swagger_auto_schema(
        operation_description="Получение списка уроков или создание нового урока",
        request_body=LessonSerializer,
        responses={
            201: LessonSerializer,
            400: 'Неверные входные данные'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    """Контроллер для просмотра списка уроков и создания уроков."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPagination

    def perform_create(self, serializer):
        """Сохраняет владельца при создании урока."""
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PaymentCreateView(APIView):
    """Создание платежа для курса"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создание платежа для оплаты курса",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса')
            },
            required=['course_id']
        ),
        responses={
            201: "Платеж создан успешно",
            400: "Ошибка при создании платежа"
        }
    )
    def post(self, request):
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "Не указан ID курса"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(pk=course_id)

            # Проверяем наличие цены у курса
            if not hasattr(course, 'price') or not course.price:
                return Response({"error": "У курса не указана цена"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Создаем продукт в Stripe
            product = create_stripe_product(course)

            # Создаем цену в Stripe
            price = create_stripe_price(product.id, course.price)

            # Создаем сессию для оплаты
            success_url = f"{request.scheme}://{request.get_host()}/api/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{request.scheme}://{request.get_host()}/api/payment/cancel"
            session = create_stripe_session(price.id, success_url, cancel_url)

            # Сохраняем информацию о платеже
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                payment_link=session.url,
                session_id=session.id,
                status="created"
            )

            return Response({
                "id": payment.id,
                "payment_link": payment.payment_link,
                "status": payment.status
            }, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response({"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(APIView):
    """Получение статуса платежа"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение статуса платежа по ID",
        manual_parameters=[
            openapi.Parameter('payment_id', openapi.IN_QUERY, description="ID платежа",
                              type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: "Статус платежа",
            404: "Платеж не найден"
        }
    )
    def get(self, request):
        payment_id = request.query_params.get('payment_id')

        if not payment_id:
            return Response({"error": "Не указан ID платежа"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(pk=payment_id, user=request.user)

            # Если есть session_id, проверяем статус в Stripe
            if payment.session_id:
                stripe_status = get_session_status(payment.session_id)

                # Обновляем статус в БД, если платеж успешный
                if stripe_status == "paid" and payment.status != "succeeded":
                    payment.status = "succeeded"
                    payment.save()

            return Response({
                "id": payment.id,
                "course": payment.course.title,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at
            })

        except Payment.DoesNotExist:
            return Response({"error": "Платеж не найден"}, status=status.HTTP_404_NOT_FOUND)


class PaymentListView(generics.ListAPIView):
    """Получение списка платежей пользователя"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение списка платежей пользователя",
        responses={
            200: "Список платежей",
        }
    )
    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        result = []

        for payment in payments:
            result.append({
                "id": payment.id,
                "course": payment.course.title,
                "amount": payment.amount,
                "status": payment.status,
                "payment_link": payment.payment_link,
                "created_at": payment.created_at
            })

        return Response(result)


class PaymentStatusCheckView(APIView):
    """Проверка детальной информации о платеже в Stripe"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение подробной информации о платеже из Stripe API",
        manual_parameters=[
            openapi.Parameter('payment_id', openapi.IN_QUERY, description="ID платежа в системе",
                              type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: "Подробная информация о платеже",
            400: "Ошибка запроса",
            404: "Платеж не найден"
        }
    )
    def get(self, request):
        payment_id = request.query_params.get('payment_id')

        if not payment_id:
            return Response({"error": "Не указан ID платежа"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Получаем платеж из БД
            payment = Payment.objects.get(id=payment_id, user=request.user)

            if not payment.session_id:
                return Response({"error": "У платежа отсутствует ID сессии Stripe"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Получаем информацию о сессии из Stripe
            session_info = retrieve_stripe_session(payment.session_id)

            if 'error' in session_info:
                return Response({"error": session_info['error']},
                                status=status.HTTP_400_BAD_REQUEST)

            # Обновляем статус платежа в нашей БД, если он изменился в Stripe
            if session_info['payment_status'] == 'paid' and payment.status != 'succeeded':
                payment.status = 'succeeded'
                payment.save()
            elif session_info['status'] == 'expired' and payment.status != 'canceled':
                payment.status = 'canceled'
                payment.save()

            # Формируем ответ
            response_data = {
                'payment_id': payment.id,
                'course': payment.course.title,
                'amount': float(payment.amount),
                'status_in_db': payment.status,
                'created_at': payment.created_at,
                'stripe_session_info': {
                    'id': session_info['id'],
                    'payment_status': session_info['payment_status'],
                    'status': session_info['status'],
                    'amount_total': session_info['amount_total'],
                    'currency': session_info['currency'],
                    'customer': session_info['customer'],
                    'payment_intent': session_info['payment_intent'],
                    'url': session_info['url'],
                    'created': datetime.datetime.fromtimestamp(
                        session_info['created']).isoformat() if session_info['created'] else None,
                    'expires_at': datetime.datetime.fromtimestamp(
                        session_info['expires_at']).isoformat() if session_info[
                        'expires_at'] else None
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Payment.DoesNotExist:
            return Response({"error": "Платеж не найден или у вас нет прав доступа к нему"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Произошла ошибка: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_update(self, serializer):
        course = self.get_object()
        four_hours_ago = timezone.now() - timedelta(hours=4)

        # Сохраняем обновленный курс
        updated_course = serializer.save()

        # Проверка на время последнего уведомления
        if not course.last_notification_sent or course.last_notification_sent < four_hours_ago:
            # Обновляем время последнего уведомления
            updated_course.last_notification_sent = timezone.now()
            updated_course.save(update_fields=['last_notification_sent'])

            # Запускаем асинхронную задачу рассылки
            send_course_update_notification.delay(updated_course.id, updated_course.title)
