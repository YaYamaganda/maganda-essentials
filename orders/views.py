from django.shortcuts import render

# Create your views here.
import json
import logging
from decimal import Decimal, ROUND_HALF_UP

import stripe
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from cart.views import get_cart
from .models import Order, OrderItem
from .services import calculate_shipping, fulfill_paid_order


logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def money(value):
    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def json_error(message, status=400):
    return JsonResponse(
        {
            "success": False,
            "error": message,
        },
        status=status,
    )


@require_GET
def checkout(request):
    cart = get_cart(request)

    items = cart.items.select_related("product")

    if not items.exists():
        return redirect("cart:cart_detail")

    subtotal = money(cart.get_total())
    shipping = calculate_shipping(subtotal)
    total = money(subtotal + shipping)

    context = {
        "cart": cart,
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "stripe_publishable_key": (
            settings.STRIPE_PUBLISHABLE_KEY
        ),
    }

    return render(
        request,
        "orders/checkout.html",
        context,
    )


@require_POST
def create_payment_intent(request):
    if (
        not settings.STRIPE_SECRET_KEY
        or not settings.STRIPE_PUBLISHABLE_KEY
    ):
        return json_error(
            "Stripe test keys are not configured.",
            status=500,
        )

    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return json_error("Invalid checkout data.")

    required_fields = [
        "email",
        "first_name",
        "last_name",
        "address_line1",
        "city",
        "state",
        "postal_code",
        "country",
    ]

    missing_fields = [
        field
        for field in required_fields
        if not str(payload.get(field, "")).strip()
    ]

    if missing_fields:
        return json_error(
            "Please complete: "
            + ", ".join(missing_fields)
        )

    cart = get_cart(request)

    cart_items = list(
        cart.items.select_related("product")
    )

    if not cart_items:
        return json_error("Your cart is empty.")

    for cart_item in cart_items:
        product = cart_item.product

        if (
            not product.is_available
            or product.stock_quantity
            < cart_item.quantity
        ):
            return json_error(
                (
                    f"Sorry, only "
                    f"{product.stock_quantity} of "
                    f"{product.name} is available."
                ),
                status=409,
            )

    subtotal = money(
        sum(
            (
                item.get_total()
                for item in cart_items
            ),
            Decimal("0.00"),
        )
    )

    shipping = calculate_shipping(subtotal)

    tax = Decimal("0.00")

    total = money(
        subtotal
        + shipping
        + tax
    )

    try:
        with transaction.atomic():
            pending_order_id = request.session.get(
                "pending_order_id"
            )

            order = None

            if pending_order_id:
                order = (
                    Order.objects
                    .select_for_update()
                    .filter(
                        pk=pending_order_id,
                        status=Order.Status.PENDING,
                        cart=cart,
                    )
                    .first()
                )

            order_values = {
                "cart": cart,
                "email": payload["email"].strip(),
                "first_name": payload[
                    "first_name"
                ].strip(),
                "last_name": payload[
                    "last_name"
                ].strip(),
                "phone": str(
                    payload.get("phone", "")
                ).strip(),
                "address_line1": payload[
                    "address_line1"
                ].strip(),
                "address_line2": str(
                    payload.get(
                        "address_line2",
                        "",
                    )
                ).strip(),
                "city": payload["city"].strip(),
                "state": payload["state"].strip(),
                "postal_code": payload[
                    "postal_code"
                ].strip(),
                "country": payload[
                    "country"
                ].strip().upper()[:2],
                "subtotal": subtotal,
                "shipping_amount": shipping,
                "tax_amount": tax,
                "total": total,
                "currency": "usd",
            }

            if order is None:
                order = Order.objects.create(
                    **order_values
                )

                request.session[
                    "pending_order_id"
                ] = order.pk
            else:
                for field, value in (
                    order_values.items()
                ):
                    setattr(order, field, value)

                order.save()

            order.items.all().delete()

            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        product=item.product,
                        product_name=(
                            item.product.name
                        ),
                        sku=item.product.sku,
                        unit_price=(
                            item.product.price
                        ),
                        quantity=item.quantity,
                        line_total=(
                            item.product.price
                            * item.quantity
                        ),
                    )
                    for item in cart_items
                ]
            )

            metadata = {
                "order_id": str(order.pk),
                "order_number": (
                    order.order_number
                ),
            }

            intent_data = {
                "amount": order.amount_in_cents,
                "currency": order.currency,
                "receipt_email": order.email,
                "description": (
                    "Maganda Essentials order "
                    f"{order.order_number}"
                ),
                "metadata": metadata,
                "shipping": {
                    "name": order.customer_name,
                    "phone": order.phone or None,
                    "address": {
                        "line1": (
                            order.address_line1
                        ),
                        "line2": (
                            order.address_line2
                            or None
                        ),
                        "city": order.city,
                        "state": order.state,
                        "postal_code": (
                            order.postal_code
                        ),
                        "country": order.country,
                    },
                },
            }

            if order.stripe_payment_intent_id:
                intent = (
                    stripe.PaymentIntent.modify(
                        order.stripe_payment_intent_id,
                        **intent_data,
                    )
                )
            else:
                intent = (
                    stripe.PaymentIntent.create(
                        **intent_data,
                        idempotency_key=(
                            "maganda-order-"
                            f"{order.order_number}"
                        ),
                    )
                )

                order.stripe_payment_intent_id = (
                    intent.id
                )

                order.save(
                    update_fields=[
                        "stripe_payment_intent_id",
                        "updated_at",
                    ]
                )

    except stripe.StripeError as exc:
        logger.exception(
            "Stripe PaymentIntent error"
        )

        user_message = (
            getattr(
                exc,
                "user_message",
                None,
            )
            or "Unable to start payment."
        )

        return json_error(
            user_message,
            status=502,
        )

    except Exception as exc:
        logger.exception(
            "Unexpected checkout error"
        )

        return json_error(
            str(exc),
            status=500,
        )

    return JsonResponse(
        {
            "success": True,
            "client_secret": (
                intent.client_secret
            ),
            "order_number": (
                order.order_number
            ),
            "return_url": (
                request.build_absolute_uri(
                    reverse(
                        "orders:payment_return"
                    )
                )
                + (
                    "?order="
                    f"{order.order_number}"
                )
            ),
        }
    )


@require_GET
def payment_return(request):
    order_number = request.GET.get(
        "order",
        "",
    )

    order = get_object_or_404(
        Order,
        order_number=order_number,
    )

    return render(
        request,
        "orders/payment_return.html",
        {
            "order": order,
        },
    )


@require_GET
def order_status(
    request,
    order_number,
):
    order = get_object_or_404(
        Order,
        order_number=order_number,
    )

    return JsonResponse(
        {
            "order_number": (
                order.order_number
            ),
            "status": order.status,
            "paid": (
                order.status
                == Order.Status.PAID
            ),
        }
    )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body

    signature = request.META.get(
        "HTTP_STRIPE_SIGNATURE",
        "",
    )

    try:
        event = (
            stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=(
                    settings
                    .STRIPE_WEBHOOK_SECRET
                ),
            )
        )

    except ValueError:
        return HttpResponse(status=400)

    except stripe.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event["type"]

    payment_intent = (
        event["data"]["object"]
    )

    order_id = (
        payment_intent
        .get("metadata", {})
        .get("order_id")
    )

    if not order_id:
        return HttpResponse(status=200)

    try:
        order = Order.objects.get(
            pk=order_id
        )

    except Order.DoesNotExist:
        logger.error(
            (
                "Stripe webhook references "
                "missing order %s"
            ),
            order_id,
        )

        return HttpResponse(status=200)

    try:
        if (
            event_type
            == "payment_intent.succeeded"
        ):
            fulfill_paid_order(
                order.pk,
                payment_intent,
            )

        elif (
            event_type
            == "payment_intent.payment_failed"
        ):
            failure_message = (
                payment_intent
                .get(
                    "last_payment_error",
                    {},
                )
                .get("message")
                or "Payment failed."
            )

            Order.objects.filter(
                pk=order.pk,
                status=Order.Status.PENDING,
            ).update(
                status=Order.Status.FAILED,
                failure_message=(
                    failure_message
                ),
            )

        elif (
            event_type
            == "payment_intent.canceled"
        ):
            Order.objects.filter(
                pk=order.pk,
                status=Order.Status.PENDING,
            ).update(
                status=Order.Status.CANCELLED
            )

    except Exception:
        logger.exception(
            (
                "Could not process Stripe "
                "event %s for order %s"
            ),
            event_type,
            order.order_number,
        )

        return HttpResponse(status=500)

    return HttpResponse(status=200)