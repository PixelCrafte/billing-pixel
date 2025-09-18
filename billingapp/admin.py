from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, Company, Client, Invoice, Quote, Receipt, 
    InvoiceLineItem, QuoteLineItem, PDFLog, AuditLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with company relationship"""
    list_display = ('email', 'first_name', 'last_name', 'company_link', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'company')
    search_fields = ('email', 'first_name', 'last_name', 'company__name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Company info', {'fields': ('company', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    def company_link(self, obj):
        if obj.company:
            url = reverse('admin:billingapp_company_change', args=[obj.company.pk])
            return format_html('<a href="{}">{}</a>', url, obj.company.name)
        return '-'
    company_link.short_description = 'Company'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Company admin with branding preview"""
    list_display = ('name', 'email', 'phone', 'city', 'country', 'user_count', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('name', 'email', 'city')
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Branding', {
            'fields': ('logo', 'logo_preview', 'primary_color', 'accent_color', 'font_family')
        }),
        ('Document Settings', {
            'fields': ('invoice_prefix', 'quote_prefix', 'receipt_prefix', 'default_currency')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px;" />',
                obj.logo.url
            )
        return 'No logo uploaded'
    logo_preview.short_description = 'Logo Preview'
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Users'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Client admin with company filtering"""
    list_display = ('name', 'email', 'company_name', 'company_link', 'created_at')
    list_filter = ('company', 'created_at')
    search_fields = ('name', 'email', 'company_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'name', 'email', 'phone')
        }),
        ('Company Details', {
            'fields': ('company_name',)
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Additional Info', {
            'fields': ('tax_number', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def company_name(self, obj):
        return obj.company_name or '-'
    company_name.short_description = 'Company Name'
    
    def company_link(self, obj):
        url = reverse('admin:billingapp_company_change', args=[obj.company.pk])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)
    company_link.short_description = 'Company'


class InvoiceLineItemInline(admin.TabularInline):
    """Inline admin for invoice line items"""
    model = InvoiceLineItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Invoice admin with line items"""
    list_display = ('number', 'client_name', 'company_link', 'status', 'issue_date', 'due_date', 'total')
    list_filter = ('status', 'company', 'issue_date', 'due_date')
    search_fields = ('number', 'client_name', 'client_email')
    readonly_fields = ('created_at', 'updated_at', 'subtotal', 'tax_total', 'total')
    inlines = [InvoiceLineItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'number', 'status')
        }),
        ('Client Info', {
            'fields': ('client_name', 'client_company', 'client_email', 'client_phone', 'client_address')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date')
        }),
        ('Financial', {
            'fields': ('currency', 'tax_rate', 'discount_rate', 'subtotal', 'tax_total', 'total')
        }),
        ('Additional Info', {
            'fields': ('payment_terms', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def company_link(self, obj):
        url = reverse('admin:billingapp_company_change', args=[obj.company.pk])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)
    company_link.short_description = 'Company'


class QuoteLineItemInline(admin.TabularInline):
    """Inline admin for quote line items"""
    model = QuoteLineItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    """Quote admin with line items"""
    list_display = ('number', 'client_name', 'company_link', 'status', 'issue_date', 'valid_until', 'total')
    list_filter = ('status', 'company', 'issue_date', 'valid_until')
    search_fields = ('number', 'client_name', 'client_email')
    readonly_fields = ('created_at', 'updated_at', 'subtotal', 'tax_total', 'total')
    inlines = [QuoteLineItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'number', 'status')
        }),
        ('Client Info', {
            'fields': ('client_name', 'client_company', 'client_email', 'client_phone', 'client_address')
        }),
        ('Dates', {
            'fields': ('issue_date', 'valid_until')
        }),
        ('Financial', {
            'fields': ('currency', 'tax_rate', 'discount_rate', 'subtotal', 'tax_total', 'total')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def company_link(self, obj):
        url = reverse('admin:billingapp_company_change', args=[obj.company.pk])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)
    company_link.short_description = 'Company'


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """Receipt admin"""
    list_display = ('number', 'client_name', 'company_link', 'amount', 'payment_method', 'issue_date')
    list_filter = ('payment_method', 'company', 'issue_date')
    search_fields = ('number', 'client_name', 'client_email', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'number', 'invoice')
        }),
        ('Client Info', {
            'fields': ('client_name', 'client_company', 'client_email', 'client_phone', 'client_address')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'payment_method', 'reference_number')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def company_link(self, obj):
        url = reverse('admin:billingapp_company_change', args=[obj.company.pk])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)
    company_link.short_description = 'Company'


@admin.register(PDFLog)
class PDFLogAdmin(admin.ModelAdmin):
    """PDF log admin for tracking generated PDFs"""
    list_display = ('document_type', 'document_id', 'company_link', 'created_at', 'expires_at', 'downloaded_at')
    list_filter = ('document_type', 'company', 'created_at', 'expires_at', 'deleted')
    search_fields = ('document_id', 'company__name')
    readonly_fields = ('download_token', 'created_at', 'downloaded_at')
    
    fieldsets = (
        ('Document Information', {
            'fields': ('document_type', 'document_id', 'company')
        }),
        ('File Information', {
            'fields': ('file_path', 'download_token')
        }),
        ('Access Control', {
            'fields': ('created_at', 'expires_at', 'downloaded_at', 'deleted')
        }),
    )
    
    def company_link(self, obj):
        url = reverse('admin:billingapp_company_change', args=[obj.company.pk])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)
    company_link.short_description = 'Company'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit log admin for tracking user actions"""
    list_display = ('action', 'user', 'company_link', 'timestamp', 'details_short')
    list_filter = ('action', 'company', 'timestamp')
    search_fields = ('action', 'user__email', 'details')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        ('Action Information', {
            'fields': ('action', 'user', 'company', 'timestamp')
        }),
        ('Details', {
            'fields': ('details',)
        }),
    )
    
    def company_link(self, obj):
        url = reverse('admin:billingapp_company_change', args=[obj.company.pk])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)
    company_link.short_description = 'Company'
    
    def details_short(self, obj):
        if obj.details and len(obj.details) > 50:
            return obj.details[:50] + '...'
        return obj.details or '-'
    details_short.short_description = 'Details'
    
    def has_add_permission(self, request):
        # Audit logs should not be manually created
        return False
    
    def has_change_permission(self, request, obj=None):
        # Audit logs should not be edited
        return False


# Customize admin site headers
admin.site.site_header = "Billing Pixel Administration"
admin.site.site_title = "Billing Pixel Admin"
admin.site.index_title = "Welcome to Billing Pixel Administration"
