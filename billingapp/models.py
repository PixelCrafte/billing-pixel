from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models import Max
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import json
import os
import secrets
from decimal import Decimal


def get_current_date():
    """Helper function to get current date for DateField default"""
    return timezone.now().date()


class User(AbstractUser):
    """Extended User model with role-based permissions"""
    
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        ACCOUNTANT = 'accountant', 'Accountant'
        USER = 'user', 'User'
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='billingapp_user_set',
        related_query_name='billingapp_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='billingapp_user_set',
        related_query_name='billingapp_user',
    )
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def has_company_permission(self, permission_type):
        """Check if user has permission for company operations"""
        if self.role in [self.Role.OWNER, self.Role.ADMIN]:
            return True
        if self.role == self.Role.ACCOUNTANT and permission_type in ['create_invoice', 'create_receipt', 'view_reports']:
            return True
        return False


class Company(models.Model):
    """Multi-tenant company model with theming support"""
    
    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
        ("GBP", "British Pound"),
        ("ZIG", "ZiG"),
        ("ZAR", "South African Rand"),
    ]
    
    FONT_CHOICES = [
        ("Inter, system-ui, sans-serif", "Inter"),
        ("Roboto, sans-serif", "Roboto"),
        ("Open Sans, sans-serif", "Open Sans"),
        ("Lato, sans-serif", "Lato"),
        ("Poppins, sans-serif", "Poppins"),
    ]
    
    # Basic Info
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_number = models.CharField(max_length=100, blank=True, null=True)

    # Contact Info
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Address
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Branding & Theming
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#6B46C1", help_text="Hex color for primary branding")
    accent_color = models.CharField(max_length=7, default="#8B5CF6", help_text="Hex color for accents") 
    font_family = models.CharField(max_length=100, choices=FONT_CHOICES, default="Inter, system-ui, sans-serif")
    
    # Business Settings
    timezone = models.CharField(max_length=50, default="UTC")
    default_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    default_vat_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Default VAT percentage"
    )
    default_discount_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)], 
        help_text="Default discount percentage"
    )
    
    # Invoice Settings
    invoice_prefix = models.CharField(max_length=10, default="INV", help_text="Prefix for invoice numbers")
    quote_prefix = models.CharField(max_length=10, default="QUO", help_text="Prefix for quote numbers")
    receipt_prefix = models.CharField(max_length=10, default="REC", help_text="Prefix for receipt numbers")
    default_terms = models.TextField(blank=True, null=True, help_text="Default terms and conditions")
    
    # Settings
    save_clients = models.BooleanField(default=True, help_text="Whether to save client details for autofill")
    
    # Subscription info (for SaaS)
    is_active = models.BooleanField(default=True)
    subscription_tier = models.CharField(max_length=20, default="basic")
    subscription_expires = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def get_rgb_primary(self):
        """Convert hex primary color to RGB for CSS variables"""
        hex_color = self.primary_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_rgb_accent(self):
        """Convert hex accent color to RGB for CSS variables"""
        hex_color = self.accent_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_primary_rgb_string(self):
        """Get primary color as comma-separated RGB string"""
        r, g, b = self.get_rgb_primary()
        return f"{r}, {g}, {b}"
    
    def get_accent_rgb_string(self):
        """Get accent color as comma-separated RGB string"""
        r, g, b = self.get_rgb_accent()
        return f"{r}, {g}, {b}"


class Client(models.Model):
    """Client records for each company (optional helpers for autofill)"""

    CURRENCY_CHOICES = Company.CURRENCY_CHOICES

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="clients")

    # Primary contact
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, db_index=True)
    phone = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    # Address fields
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    tax_number = models.CharField(max_length=100, blank=True, null=True)

    # Optional defaults for forms
    default_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True, null=True)
    default_vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    default_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    notes = models.TextField(blank=True, null=True)
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

    def __str__(self):
        if self.company_name:
            return f"{self.name} — {self.company_name}"
        return self.name

    @property
    def display_name(self):
        """Nice display name for autofill lists"""
        if self.company_name:
            return f"{self.company_name} ({self.name})"
        return self.name

    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [
            self.address_line1 or "",
            self.address_line2 or "",
            self.city or "",
            self.state or "",
            self.postal_code or "",
            self.country or "",
        ]
        return ", ".join([p for p in parts if p])


class InvoiceTemplate(models.Model):
    """Optional custom invoice templates per company"""
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invoice_templates")
    name = models.CharField(max_length=100)
    html_template = models.TextField(help_text="Custom HTML template for PDF generation")
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['company', 'name']
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class BaseDocument(models.Model):
    """Abstract base class for invoices, quotes, and receipts"""
    
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        VIEWED = "viewed", "Viewed"
        PAID = "paid", "Paid"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    CURRENCY_CHOICES = Company.CURRENCY_CHOICES

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="%(class)s_created")

    # Client info (stored inline for versioning)
    client_name = models.CharField(max_length=255)
    client_company = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)

    # Document details
    number = models.CharField(max_length=50, unique=True, blank=True)
    issue_date = models.DateField(default=get_current_date)
    due_date = models.DateField(blank=True, null=True)

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="USD")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    notes = models.TextField(blank=True, null=True)
    
    # Versioned data for PDF regeneration
    versioned_data = models.JSONField(default=dict, help_text="Snapshot of document data at time of generation")
    metadata = models.JSONField(default=dict, help_text="Additional metadata")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    @property 
    def subtotal(self):
        """Calculate subtotal from line items"""
        return sum(item.line_total for item in self.items.all())
    
    @property
    def tax_total(self):
        """Calculate tax amount"""
        return (self.subtotal * self.tax_rate) / 100
    
    @property
    def discount_total(self):
        """Calculate discount amount"""
        return (self.subtotal * self.discount_rate) / 100
    
    @property
    def total(self):
        """Calculate final total"""
        return self.subtotal + self.tax_total - self.discount_total
    
    def lock_version_data(self):
        """Lock current state into versioned_data for PDF generation"""
        self.versioned_data = {
            'company': {
                'name': self.company.name,
                'email': self.company.email,
                'phone': self.company.phone,
                'address_line1': self.company.address_line1,
                'address_line2': self.company.address_line2,
                'city': self.company.city,
                'state': self.company.state,
                'postal_code': self.company.postal_code,
                'country': self.company.country,
                'logo_url': self.company.logo.url if self.company.logo else None,
                'primary_color': self.company.primary_color,
                'accent_color': self.company.accent_color,
                'font_family': self.company.font_family,
            },
            'client': {
                'name': self.client_name,
                'company': self.client_company,
                'email': self.client_email,
                'phone': self.client_phone,
                'address': self.client_address,
            },
            'document': {
                'number': self.number,
                'issue_date': self.issue_date.isoformat(),
                'due_date': self.due_date.isoformat() if self.due_date else None,
                'currency': self.currency,
                'tax_rate': float(self.tax_rate),
                'discount_rate': float(self.discount_rate),
                'notes': self.notes,
            },
            'items': [
                {
                    'description': item.description,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'discount': float(item.discount) if hasattr(item, 'discount') else 0,
                    'line_total': float(item.line_total),
                }
                for item in self.items.all()
            ],
            'totals': {
                'subtotal': float(self.subtotal),
                'tax_total': float(self.tax_total),
                'discount_total': float(self.discount_total),
                'total': float(self.total),
            },
            'locked_at': timezone.now().isoformat(),
        }
        self.save(update_fields=['versioned_data'])


class Invoice(BaseDocument):
    """Invoice model with auto-numbering and PDF generation"""

    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.number:
            year = timezone.now().year
            prefix = f"{self.company.invoice_prefix}-{year}-"
            
            last_invoice = Invoice.objects.filter(
                company=self.company,
                number__startswith=prefix
            ).aggregate(Max("number"))
            
            last_number = last_invoice["number__max"]
            
            if last_number:
                last_seq = int(last_number.split("-")[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
                
            self.number = f"{prefix}{new_seq:04d}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} - {self.client_name}"
    
    def get_absolute_url(self):
        return reverse('billingapp:invoice_detail', kwargs={'pk': self.pk})


class InvoiceLineItem(models.Model):
    """Line items for invoices"""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount percentage")
    
    @property
    def line_total(self):
        """Calculate line total with discount"""
        subtotal = self.quantity * self.unit_price
        discount_amount = (subtotal * self.discount) / 100
        return subtotal - discount_amount

    def __str__(self):
        return f"{self.description} ({self.quantity} x ${self.unit_price})"


class Quote(BaseDocument):
    """Quotation model"""

    valid_until = models.DateField(blank=True, null=True)
    converted_to_invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.number:
            year = timezone.now().year
            prefix = f"{self.company.quote_prefix}-{year}-"
            
            last_quote = Quote.objects.filter(
                company=self.company,
                number__startswith=prefix
            ).aggregate(Max("number"))
            
            last_number = last_quote["number__max"]
            
            if last_number:
                last_seq = int(last_number.split("-")[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
                
            self.number = f"{prefix}{new_seq:04d}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} - {self.client_name}"
    
    def convert_to_invoice(self):
        """Convert this quote to an invoice"""
        if self.converted_to_invoice:
            return self.converted_to_invoice
            
        invoice = Invoice.objects.create(
            company=self.company,
            created_by=self.created_by,
            client_name=self.client_name,
            client_company=self.client_company,
            client_email=self.client_email,
            client_phone=self.client_phone,
            client_address=self.client_address,
            currency=self.currency,
            tax_rate=self.tax_rate,
            discount_rate=self.discount_rate,
            notes=self.notes,
            due_date=self.due_date,
        )
        
        # Copy line items
        for item in self.items.all():
            InvoiceLineItem.objects.create(
                invoice=invoice,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
            )
        
        self.converted_to_invoice = invoice
        self.save(update_fields=['converted_to_invoice'])
        
        return invoice


class QuoteLineItem(models.Model):
    """Line items for quotes"""
    
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="items")
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    @property
    def line_total(self):
        """Calculate line total with discount"""
        subtotal = self.quantity * self.unit_price
        discount_amount = (subtotal * self.discount) / 100
        return subtotal - discount_amount

    def __str__(self):
        return f"{self.description} ({self.quantity} x ${self.unit_price})"


class Receipt(BaseDocument):
    """Receipt model for payment tracking"""

    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="receipts")
    payment_method = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="E.g. Cash, Bank Transfer, Card, Mobile Money"
    )
    reference_number = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Transaction reference from bank or payment system"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.number:
            year = timezone.now().year
            prefix = f"{self.company.receipt_prefix}-{year}-"
            
            last_receipt = Receipt.objects.filter(
                company=self.company,
                number__startswith=prefix
            ).aggregate(Max("number"))
            
            last_number = last_receipt["number__max"]
            
            if last_number:
                last_seq = int(last_number.split("-")[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
                
            self.number = f"{prefix}{new_seq:04d}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} - ${self.amount}"


class PDFLog(models.Model):
    """Track PDF generation and downloads with secure tokens"""
    
    class DocumentType(models.TextChoices):
        INVOICE = 'invoice', 'Invoice'
        QUOTE = 'quote', 'Quote' 
        RECEIPT = 'receipt', 'Receipt'
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="pdf_logs")
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    document_id = models.PositiveIntegerField()
    
    file_path = models.CharField(max_length=500, blank=True, null=True)
    download_token = models.CharField(max_length=64, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    downloaded_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['download_token']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['company', 'document_type', 'document_id']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.download_token:
            self.download_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.document_type} PDF - {self.download_token[:8]}..."
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_downloaded(self):
        return self.downloaded_at is not None


class AuditLog(models.Model):
    """Basic audit logging for accountability"""
    
    class Action(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        SEND = 'send', 'Send'
        VIEW = 'view', 'View'
        DOWNLOAD = 'download', 'Download'
        PAYMENT = 'payment', 'Payment'
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="audit_logs")
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=20, choices=Action.choices)
    
    # Generic foreign key fields for any model
    content_type = models.CharField(max_length=50)  # e.g., 'invoice', 'quote'
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(max_length=200)  # String representation
    
    details = models.JSONField(default=dict, blank=True)  # Additional context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['company', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} {self.action} {self.content_type} {self.object_repr}"