from django.db import models

# Create your models here.
import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone

from cart.models import Cart
from products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    order_number = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
    )

    cart = models.ForeignKey(
        Cart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    email = models.EmailField()

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    address_line1 = models.CharField(
        max_length=255,
    )

    address_line2 = models.CharField(
        max_length=255,
        blank=True,
    )

    city = models.CharField(
        max_length=120,
    )

    state = models.CharField(
        max_length=80,
    )

    postal_code = models.CharField(
        max_length=20,
    )

    country = models.CharField(
        max_length=2,
        default="US",
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    shipping_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    currency = models.CharField(
        max_length=3,
        default="usd",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
    )

    stripe_latest_charge_id = models.CharField(
        max_length=255,
        blank=True,
    )

    inventory_processed = models.BooleanField(
        default=False,
    )

    confirmation_email_sent = models.BooleanField(
        default=False,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failure_message = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.order_number} - "
            f"{self.email}"
        )

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = (
                f"MGD-"
                f"{timezone.now():%Y%m%d}-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )

        super().save(*args, **kwargs)

    @property
    def customer_name(self):
        return (
            f"{self.first_name} "
            f"{self.last_name}"
        ).strip()

    @property
    def amount_in_cents(self):
        return int(self.total * 100)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )

    product_name = models.CharField(
        max_length=200,
    )

    sku = models.CharField(
        max_length=100,
        blank=True,
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField()

    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return (
            f"{self.quantity} × "
            f"{self.product_name}"
        )

    def save(self, *args, **kwargs):
        self.line_total = (
            self.unit_price
            * self.quantity
        )

        super().save(*args, **kwargs)