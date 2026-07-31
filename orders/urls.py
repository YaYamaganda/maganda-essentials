from django.urls import path

from . import views


app_name = "orders"


urlpatterns = [
    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),
    path(
        "create-payment-intent/",
        views.create_payment_intent,
        name="create_payment_intent",
    ),
    path(
        "payment-return/",
        views.payment_return,
        name="payment_return",
    ),
    path(
        "status/<str:order_number>/",
        views.order_status,
        name="order_status",
    ),
    path(
        "stripe/webhook/",
        views.stripe_webhook,
        name="stripe_webhook",
    ),
]