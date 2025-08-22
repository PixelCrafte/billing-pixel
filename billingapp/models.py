from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models import Max

class User(AbstractUser):
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.username
    
class Company(models.Model):
    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("ZIG", "ZiG"),
    ]
    
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_number = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    theme_color = models.CharField(max_length=20, default="#000000")

    # Default settings for billing
    default_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    default_vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Default VAT percentage")
    default_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Default discount percentage")
    save_clients = models.BooleanField(default=True, help_text="Whether to save client details for autofill")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.default_currency})"

class Quotation(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"

    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="quotations")

    client_name = models.CharField(max_length=255)
    client_company = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)

    quotation_number = models.CharField(max_length=20, unique=True, blank=True)
    date_issued = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)

    currency = models.CharField(
        max_length=3,
        choices=[("USD", "US Dollar"), ("ZIG", "ZiG")],
        default="USD"
    )

    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.quotation_number:  # Auto-generate only if user didn’t provide
            year = timezone.now().year
            prefix = f"QUO-{year}-"

            # Find the highest sequence for the current year
            last_quote = Quotation.objects.filter(
                quotation_number__startswith=prefix
            ).aggregate(Max("quotation_number"))

            last_number = last_quote["quotation_number__max"]

            if last_number:
                # Extract last sequence
                last_seq = int(last_number.split("-")[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1

            self.quotation_number = f"{prefix}{new_seq:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quotation_number} ({self.client_name})"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def amount(self):
        return self.quantity * self.rate

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.rate})"

class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"

    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="invoices")

    client_name = models.CharField(max_length=255)
    client_company = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)

    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    date_issued = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)

    currency = models.CharField(
        max_length=3,
        choices=[("USD", "US Dollar"), ("ZIG", "ZiG")],
        default="USD"
    )

    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = timezone.now().year
            prefix = f"INV-{year}-"

            # Find the last invoice for this year
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=prefix
            ).aggregate(Max("invoice_number"))

            last_number = last_invoice["invoice_number__max"]

            if last_number:
                last_seq = int(last_number.split("-")[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1

            self.invoice_number = f"{prefix}{new_seq:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} ({self.client_name})"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2)  # price per unit
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # quantity * rate

    def save(self, *args, **kwargs):
        # Auto calculate amount if not provided
        if not self.amount:
            self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.rate})"
    

class Receipt(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        CANCELLED = "cancelled", "Cancelled"

    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="receipts")

    client_name = models.CharField(max_length=255)
    client_company = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)

    receipt_number = models.CharField(max_length=20, unique=True, blank=True)
    date_issued = models.DateField(auto_now_add=True)

    currency = models.CharField(
        max_length=3,
        choices=[("USD", "US Dollar"), ("ZIG", "ZiG")],
        default="USD"
    )

    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="E.g. Cash, Bank Transfer, Card, Mobile Money"
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction reference from bank or payment system"
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ISSUED
    )

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            year = timezone.now().year
            prefix = f"REC-{year}-"

            last_receipt = Receipt.objects.filter(
                receipt_number__startswith=prefix
            ).aggregate(Max("receipt_number"))

            last_number = last_receipt["receipt_number__max"]

            if last_number:
                last_seq = int(last_number.split("-")[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1

            self.receipt_number = f"{prefix}{new_seq:04d}"

        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return sum(item.amount for item in self.items.all())

    def __str__(self):
        return f"{self.receipt_number} ({self.client_name})"


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="items")
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2)  # price per unit
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto calculate amount if not provided
        if not self.amount:
            self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.rate})"

from django.db import models
from django.utils import timezone
from decimal import Decimal

class Client(models.Model):
    """
    Client objects belong to a Company (tenant). These are *optional* helpers for autofill
    in the frontend — other models (Invoice/Receipt/Quotation) will still store client
    details inline as you requested.
    """

    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("ZIG", "ZiG"),
    ]

    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="clients")

    # Primary contact
    name = models.CharField(max_length=255)

    # Client's business / organisation name (optional)
    company_name = models.CharField(max_length=255, blank=True, null=True)

    email = models.EmailField(blank=True, null=True, db_index=True)
    phone = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    # Address fields (kept optional because some businesses don't want to link clients)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    tax_number = models.CharField(max_length=100, blank=True, null=True)

    # Optional defaults that can be used to pre-populate forms
    default_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True, null=True)
    default_vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    default_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    notes = models.TextField(blank=True, null=True)

    # Soft delete / active toggle (handy for UX)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "email"]),
            models.Index(fields=["company", "phone"]),
            models.Index(fields=["company", "name"]),
        ]
        # If you want to prevent exact duplicate (company + email) when email exists:
        # constraints = [
        #     models.UniqueConstraint(fields=["company", "email"], name="unique_company_client_email", condition=~models.Q(email=None))
        # ]

    def __str__(self):
        if self.company_name:
            return f"{self.name} — {self.company_name}"
        return self.name

    @property
    def display_name(self):
        """Nice display name for autofill lists."""
        if self.company_name:
            return f"{self.company_name} ({self.name})"
        return self.name

    @property
    def full_address(self):
        parts = [
            self.address_line1 or "",
            self.address_line2 or "",
            self.city or "",
            self.state or "",
            self.postal_code or "",
            self.country or "",
        ]
        return ", ".join([p for p in parts if p])

    @classmethod
    def get_or_create_from_payload(cls, company, payload):
        """
        Helper for the autofill/save flow.

        payload: dict-like with keys matching Client fields (name, company_name, email, phone, etc.)

        Lookup priority:
          1. email (case-insensitive)
          2. phone
          3. name + company_name

        Returns: (client_instance, created_bool)
        """
        email = (payload.get("email") or "").strip() or None
        phone = (payload.get("phone") or "").strip() or None
        name = (payload.get("name") or "").strip() or None
        company_name = (payload.get("company_name") or "").strip() or None

        client = None

        if email:
            client = cls.objects.filter(company=company, email__iexact=email).first()
        if not client and phone:
            client = cls.objects.filter(company=company, phone=phone).first()
        if not client and name:
            qs = cls.objects.filter(company=company, name__iexact=name)
            if company_name:
                qs = qs.filter(company_name__iexact=company_name)
            client = qs.first()

        defaults = {
            "name": name or payload.get("name"),
            "company_name": company_name or payload.get("company_name"),
            "email": email,
            "phone": phone,
            "address_line1": payload.get("address_line1"),
            "address_line2": payload.get("address_line2"),
            "city": payload.get("city"),
            "state": payload.get("state"),
            "postal_code": payload.get("postal_code"),
            "country": payload.get("country"),
            "tax_number": payload.get("tax_number"),
            "default_currency": payload.get("default_currency"),
            "default_vat_rate": payload.get("default_vat_rate", Decimal("0.00")),
            "default_discount_rate": payload.get("default_discount_rate", Decimal("0.00")),
            "notes": payload.get("notes"),
            "is_active": True,
            "updated_at": timezone.now(),
        }

        if client:
            # Update fields that are present in payload
            for key, value in defaults.items():
                # only update if value is not None (avoid blanking existing info)
                if value not in (None, ""):
                    setattr(client, key, value)
            client.save()
            return client, False

        # create new client
        data = {k: v for k, v in defaults.items() if v not in (None, "")}
        data["company"] = company
        client = cls.objects.create(**data)
        return client, True