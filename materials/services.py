import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course):
    """Создание продукта в Stripe"""
    product = stripe.Product.create(
        name=course.title,
        description=course.description or 'Курс на платформе LMS'
    )
    return product


def create_stripe_price(product_id, amount):
    """Создание цены в Stripe"""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),  # Цена в копейках
        currency="rub",
    )
    return price


def create_stripe_session(price_id, success_url, cancel_url):
    """Создание сессии для оплаты"""
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session


def get_session_status(session_id):
    """Получение статуса сессии"""
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status


def retrieve_stripe_session(session_id):
    """
    Получение полной информации о сессии оплаты

    Документация: https://stripe.com/docs/api/checkout/sessions/retrieve
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'id': session.id,
            'object': session.object,
            'payment_status': session.payment_status,
            'status': session.status,
            'amount_total': session.amount_total / 100 if session.amount_total else None,
            'currency': session.currency,
            'customer': session.customer,
            'customer_details': session.customer_details if hasattr(session,
                                                                    'customer_details') else None,
            'payment_intent': session.payment_intent,
            'url': session.url,
            'created': session.created,
            'expires_at': session.expires_at
        }
    except stripe.error.StripeError as e:
        return {'error': str(e)}