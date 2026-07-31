from decimal import Decimal


def calculate_shipping(subtotal):
    free_shipping_threshold = Decimal("50.00")
    standard_shipping_fee = Decimal("6.95")

    if subtotal >= free_shipping_threshold:
        return Decimal("0.00")

    return standard_shipping_fee


def fulfill_paid_order(
    order_id,
    payment_intent,
):
    from django.utils import timezone

    from .models import Order

    order = Order.objects.get(
        pk=order_id
    )

    order.status = Order.Status.PAID
    order.paid_at = timezone.now()

    order.save(
        update_fields=[
            "status",
            "paid_at",
            "updated_at",
        ]
    )

    if order.cart:
        order.cart.clear()

    return order