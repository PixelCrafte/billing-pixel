from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
import re

from .models import User, Company, Client, Invoice, Quote, Receipt, InvoiceLineItem, QuoteLineItem


class UserRegistrationForm(UserCreationForm):
    """User registration form with enhanced validation"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """User login form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise ValidationError("Invalid email or password.")
        
        return cleaned_data


class CompanySetupForm(forms.ModelForm):
    """Company setup form for new users"""
    class Meta:
        model = Company
        fields = [
            'name', 'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'primary_color', 'secondary_color', 'logo',
            'invoice_prefix', 'quote_prefix', 'receipt_prefix',
            'default_payment_terms', 'currency'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'company@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.company.com'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apt, Suite, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'invoice_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INV-'}),
            'quote_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'QUO-'}),
            'receipt_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'REC-'}),
            'default_payment_terms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '30'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
        }
    
    def clean_primary_color(self):
        color = self.cleaned_data.get('primary_color')
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValidationError("Invalid color format. Use hex format like #FF0000")
        return color
    
    def clean_secondary_color(self):
        color = self.cleaned_data.get('secondary_color')
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValidationError("Invalid color format. Use hex format like #FF0000")
        return color


class ClientForm(forms.ModelForm):
    """Client creation and editing form"""
    class Meta:
        model = Client
        fields = [
            'name', 'email', 'phone', 'company',
            'address', 'tax_number', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name (Optional)'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tax ID / VAT Number'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Internal notes about this client'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            queryset = Client.objects.filter(email=email, company=self.company)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("A client with this email already exists in your company.")
        return email


class LineItemFormSet(forms.BaseInlineFormSet):
    """Base formset for line items with validation"""
    
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        
        total_forms = len([form for form in self.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False)])
        if total_forms < 1:
            raise ValidationError("At least one line item is required.")


class InvoiceLineItemForm(forms.ModelForm):
    """Form for invoice line items"""
    class Meta:
        model = InvoiceLineItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }


class InvoiceForm(forms.ModelForm):
    """Invoice creation and editing form"""
    class Meta:
        model = Invoice
        fields = [
            'client', 'issue_date', 'due_date', 'currency',
            'tax_rate', 'discount_amount', 'notes'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Payment instructions or additional notes'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if self.company:
            self.fields['client'].queryset = Client.objects.filter(company=self.company)
        
        # Set default dates
        if not self.instance.pk:
            self.fields['issue_date'].initial = timezone.now().date()
            self.fields['due_date'].initial = timezone.now().date() + timedelta(days=30)
    
    def clean_due_date(self):
        issue_date = self.cleaned_data.get('issue_date')
        due_date = self.cleaned_data.get('due_date')
        
        if issue_date and due_date and due_date < issue_date:
            raise ValidationError("Due date cannot be earlier than issue date.")
        
        return due_date


class QuoteLineItemForm(forms.ModelForm):
    """Form for quote line items"""
    class Meta:
        model = QuoteLineItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item description'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }


class QuoteForm(forms.ModelForm):
    """Quote creation and editing form"""
    class Meta:
        model = Quote
        fields = [
            'client', 'issue_date', 'valid_until', 'currency',
            'tax_rate', 'discount_amount', 'notes'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Terms and conditions or additional notes'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if self.company:
            self.fields['client'].queryset = Client.objects.filter(company=self.company)
        
        # Set default dates
        if not self.instance.pk:
            self.fields['issue_date'].initial = timezone.now().date()
            self.fields['valid_until'].initial = timezone.now().date() + timedelta(days=30)
    
    def clean_valid_until(self):
        issue_date = self.cleaned_data.get('issue_date')
        valid_until = self.cleaned_data.get('valid_until')
        
        if issue_date and valid_until and valid_until < issue_date:
            raise ValidationError("Valid until date cannot be earlier than issue date.")
        
        return valid_until


class ReceiptForm(forms.ModelForm):
    """Receipt creation and editing form"""
    class Meta:
        model = Receipt
        fields = [
            'client', 'invoice', 'amount', 'currency',
            'payment_method', 'reference_number', 'notes'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'invoice': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction ID or check number'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Payment notes'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if self.company:
            self.fields['client'].queryset = Client.objects.filter(company=self.company)
            self.fields['invoice'].queryset = Invoice.objects.filter(company=self.company, status='sent')
            self.fields['invoice'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        invoice = cleaned_data.get('invoice')
        
        if invoice and invoice.client != client:
            raise ValidationError("The selected invoice does not belong to the selected client.")
        
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """User profile editing form"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            queryset = User.objects.filter(email=email)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("A user with this email already exists.")
        return email


class PasswordChangeForm(DjangoPasswordChangeForm):
    """Enhanced password change form"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )


# Formsets for inline editing
InvoiceLineItemFormSet = forms.inlineformset_factory(
    Invoice,
    InvoiceLineItem,
    form=InvoiceLineItemForm,
    formset=LineItemFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)

QuoteLineItemFormSet = forms.inlineformset_factory(
    Quote,
    QuoteLineItem,
    form=QuoteLineItemForm,
    formset=LineItemFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


# Legacy form for backward compatibility
class SignUpForm(UserRegistrationForm):
    """Backward compatibility alias"""
    pass
