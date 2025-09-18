from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import json
from datetime import datetime, timedelta
import logging

from .models import (
    User, Company, Client, Invoice, Quote, Receipt, PDFLog, AuditLog
)
from .forms import (
    UserRegistrationForm, UserLoginForm, CompanySetupForm, ClientForm,
    InvoiceForm, QuoteForm, ReceiptForm, UserProfileForm, PasswordChangeForm
)
from .permissions import (
    require_company_permission, CompanyPermissionMixin,
    can_view_document, can_edit_document, can_delete_document
)
from .utils import (
    create_pdf_for_document, serve_pdf_download, generate_next_number
)

logger = logging.getLogger(__name__)


# Authentication Views
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('billing:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'billing:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'billingapp/login.html', {'form': form})


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('billing:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('billing:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'billingapp/signup.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('billing:login')


# Dashboard and Home Views
@login_required
def home_view(request):
    """Dashboard home view"""
    if not hasattr(request.user, 'company') or not request.user.company:
        return redirect('billing:company_setup')
    
    company = request.user.company
    
    # Dashboard statistics
    total_invoices = Invoice.objects.filter(company=company).count()
    total_quotes = Quote.objects.filter(company=company).count()
    total_receipts = Receipt.objects.filter(company=company).count()
    total_clients = Client.objects.filter(company=company).count()
    
    # Recent activity
    recent_invoices = Invoice.objects.filter(company=company).order_by('-created_at')[:5]
    recent_quotes = Quote.objects.filter(company=company).order_by('-created_at')[:5]
    recent_receipts = Receipt.objects.filter(company=company).order_by('-created_at')[:5]
    
    # Financial summary
    total_invoice_amount = Invoice.objects.filter(
        company=company, status='sent'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    total_receipt_amount = Receipt.objects.filter(
        company=company
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'total_invoices': total_invoices,
        'total_quotes': total_quotes,
        'total_receipts': total_receipts,
        'total_clients': total_clients,
        'recent_invoices': recent_invoices,
        'recent_quotes': recent_quotes,
        'recent_receipts': recent_receipts,
        'total_invoice_amount': total_invoice_amount,
        'total_receipt_amount': total_receipt_amount,
    }
    
    return render(request, 'billingapp/home.html', context)


@login_required
def company_setup_view(request):
    """Company setup view for new users"""
    if hasattr(request.user, 'company') and request.user.company:
        return redirect('billing:home')
    
    if request.method == 'POST':
        form = CompanySetupForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            request.user.company = company
            request.user.role = 'owner'
            request.user.save()
            
            AuditLog.objects.create(
                company=company,
                user=request.user,
                action='company_created',
                details=f'Company "{company.name}" created'
            )
            
            messages.success(request, f'Company "{company.name}" has been set up successfully!')
            return redirect('billing:home')
    else:
        form = CompanySetupForm()
    
    return render(request, 'billingapp/company_setup.html', {'form': form})


# Client Management Views
class ClientListView(LoginRequiredMixin, CompanyPermissionMixin, ListView):
    """List all clients for the company"""
    model = Client
    template_name = 'billingapp/clientele.html'
    context_object_name = 'clients'
    paginate_by = 20
    required_permissions = ['view_client']
    
    def get_queryset(self):
        queryset = Client.objects.filter(company=self.request.user.company)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company__icontains=search)
            )
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@login_required
@require_company_permission(['add_client'])
def client_create_view(request):
    """Create a new client"""
    if request.method == 'POST':
        form = ClientForm(request.POST, company=request.user.company)
        if form.is_valid():
            client = form.save(commit=False)
            client.company = request.user.company
            client.save()
            
            AuditLog.objects.create(
                company=request.user.company,
                user=request.user,
                action='client_created',
                details=f'Client "{client.name}" created'
            )
            
            messages.success(request, f'Client "{client.name}" has been created successfully!')
            return redirect('billing:clients')
    else:
        form = ClientForm(company=request.user.company)
    
    return render(request, 'billingapp/client_form.html', {
        'form': form, 
        'title': 'Add New Client'
    })


@login_required
@require_company_permission(['change_client'])
def client_edit_view(request, client_id):
    """Edit an existing client"""
    client = get_object_or_404(Client, id=client_id, company=request.user.company)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client, company=request.user.company)
        if form.is_valid():
            client = form.save()
            
            AuditLog.objects.create(
                company=request.user.company,
                user=request.user,
                action='client_updated',
                details=f'Client "{client.name}" updated'
            )
            
            messages.success(request, f'Client "{client.name}" has been updated successfully!')
            return redirect('billing:clients')
    else:
        form = ClientForm(instance=client, company=request.user.company)
    
    return render(request, 'billingapp/client_form.html', {
        'form': form, 
        'client': client,
        'title': 'Edit Client'
    })


@login_required
@require_company_permission(['delete_client'])
def client_delete_view(request, client_id):
    """Delete a client"""
    client = get_object_or_404(Client, id=client_id, company=request.user.company)
    
    if request.method == 'POST':
        client_name = client.name
        client.delete()
        
        AuditLog.objects.create(
            company=request.user.company,
            user=request.user,
            action='client_deleted',
            details=f'Client "{client_name}" deleted'
        )
        
        messages.success(request, f'Client "{client_name}" has been deleted successfully!')
        return redirect('billing:clients')
    
    return render(request, 'billingapp/client_confirm_delete.html', {'client': client})


# Invoice Management Views
class InvoiceListView(LoginRequiredMixin, CompanyPermissionMixin, ListView):
    """List all invoices for the company"""
    model = Invoice
    template_name = 'billingapp/invoices.html'
    context_object_name = 'invoices'
    paginate_by = 20
    required_permissions = ['view_invoice']
    
    def get_queryset(self):
        queryset = Invoice.objects.filter(company=self.request.user.company)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(client__name__icontains=search) |
                Q(client__company__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = Invoice.STATUS_CHOICES
        return context


@login_required
@require_company_permission(['add_invoice'])
def invoice_create_view(request):
    """Create a new invoice"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST, company=request.user.company)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.company = request.user.company
            invoice.number = generate_next_number(request.user.company, 'invoice')
            invoice.save()
            form.save_m2m()  # Save many-to-many relationships
            
            AuditLog.objects.create(
                company=request.user.company,
                user=request.user,
                action='invoice_created',
                details=f'Invoice "{invoice.number}" created'
            )
            
            messages.success(request, f'Invoice "{invoice.number}" has been created successfully!')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm(company=request.user.company)
    
    return render(request, 'billingapp/invoice.html', {
        'form': form,
        'title': 'Create New Invoice'
    })


@login_required
def invoice_detail_view(request, invoice_id):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, id=invoice_id, company=request.user.company)
    
    if not can_view_document(request.user, invoice):
        raise Http404("Invoice not found")
    
    return render(request, 'billingapp/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_edit_view(request, invoice_id):
    """Edit an existing invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id, company=request.user.company)
    
    if not can_edit_document(request.user, invoice):
        messages.error(request, 'You do not have permission to edit this invoice.')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice, company=request.user.company)
        if form.is_valid():
            invoice = form.save()
            
            AuditLog.objects.create(
                company=request.user.company,
                user=request.user,
                action='invoice_updated',
                details=f'Invoice "{invoice.number}" updated'
            )
            
            messages.success(request, f'Invoice "{invoice.number}" has been updated successfully!')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm(instance=invoice, company=request.user.company)
    
    return render(request, 'billingapp/invoice.html', {
        'form': form,
        'invoice': invoice,
        'title': 'Edit Invoice'
    })


# Quote Management Views
class QuoteListView(LoginRequiredMixin, CompanyPermissionMixin, ListView):
    """List all quotes for the company"""
    model = Quote
    template_name = 'billingapp/quotes.html'
    context_object_name = 'quotes'
    paginate_by = 20
    required_permissions = ['view_quote']
    
    def get_queryset(self):
        queryset = Quote.objects.filter(company=self.request.user.company)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(client__name__icontains=search) |
                Q(client__company__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = Quote.STATUS_CHOICES
        return context


@login_required
@require_company_permission(['add_quote'])
def quote_create_view(request):
    """Create a new quote"""
    if request.method == 'POST':
        form = QuoteForm(request.POST, company=request.user.company)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.company = request.user.company
            quote.number = generate_next_number(request.user.company, 'quote')
            quote.save()
            form.save_m2m()
            
            AuditLog.objects.create(
                company=request.user.company,
                user=request.user,
                action='quote_created',
                details=f'Quote "{quote.number}" created'
            )
            
            messages.success(request, f'Quote "{quote.number}" has been created successfully!')
            return redirect('billing:quote_detail', quote_id=quote.id)
    else:
        form = QuoteForm(company=request.user.company)
    
    return render(request, 'billingapp/quotation.html', {
        'form': form,
        'title': 'Create New Quote'
    })


@login_required
def quote_detail_view(request, quote_id):
    """View quote details"""
    quote = get_object_or_404(Quote, id=quote_id, company=request.user.company)
    
    if not can_view_document(request.user, quote):
        raise Http404("Quote not found")
    
    return render(request, 'billingapp/quote_detail.html', {'quote': quote})


# Receipt Management Views
class ReceiptListView(LoginRequiredMixin, CompanyPermissionMixin, ListView):
    """List all receipts for the company"""
    model = Receipt
    template_name = 'billingapp/receipts.html'
    context_object_name = 'receipts'
    paginate_by = 20
    required_permissions = ['view_receipt']
    
    def get_queryset(self):
        queryset = Receipt.objects.filter(company=self.request.user.company)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(client__name__icontains=search) |
                Q(client__company__icontains=search) |
                Q(invoice__number__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@login_required
@require_company_permission(['add_receipt'])
def receipt_create_view(request):
    """Create a new receipt"""
    if request.method == 'POST':
        form = ReceiptForm(request.POST, company=request.user.company)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.company = request.user.company
            receipt.number = generate_next_number(request.user.company, 'receipt')
            receipt.save()
            
            AuditLog.objects.create(
                company=request.user.company,
                user=request.user,
                action='receipt_created',
                details=f'Receipt "{receipt.number}" created'
            )
            
            messages.success(request, f'Receipt "{receipt.number}" has been created successfully!')
            return redirect('billing:receipt_detail', receipt_id=receipt.id)
    else:
        form = ReceiptForm(company=request.user.company)
    
    return render(request, 'billingapp/receipt.html', {
        'form': form,
        'title': 'Create New Receipt'
    })


@login_required
def receipt_detail_view(request, receipt_id):
    """View receipt details"""
    receipt = get_object_or_404(Receipt, id=receipt_id, company=request.user.company)
    
    if not can_view_document(request.user, receipt):
        raise Http404("Receipt not found")
    
    return render(request, 'billingapp/receipt_detail.html', {'receipt': receipt})


# PDF Generation Views
@login_required
def generate_pdf_view(request, document_type, document_id):
    """Generate PDF for a document"""
    if document_type not in ['invoice', 'quote', 'receipt']:
        raise Http404("Invalid document type")
    
    model_map = {
        'invoice': Invoice,
        'quote': Quote,
        'receipt': Receipt
    }
    
    model = model_map[document_type]
    document = get_object_or_404(model, id=document_id, company=request.user.company)
    
    if not can_view_document(request.user, document):
        raise Http404("Document not found")
    
    try:
        pdf_log = create_pdf_for_document(document, request.user)
        
        AuditLog.objects.create(
            company=request.user.company,
            user=request.user,
            action='pdf_generated',
            details=f'PDF generated for {document_type} "{document.number}"'
        )
        
        return serve_pdf_download(pdf_log.token)
    
    except Exception as e:
        logger.error(f"Error generating PDF for {document_type} {document_id}: {str(e)}")
        messages.error(request, 'Error generating PDF. Please try again.')
        return redirect(f'billing:{document_type}_detail', **{f'{document_type}_id': document_id})


@login_required
def download_pdf_view(request, token):
    """Download PDF using secure token"""
    return serve_pdf_download(token)


# Profile and Settings Views
@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('billing:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'billingapp/profile.html', {'form': form})


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('billing:profile')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'billingapp/change-password.html', {'form': form})


# API Views for AJAX requests
@login_required
@require_http_methods(["GET"])
def api_clients_view(request):
    """API endpoint to get clients for the company"""
    clients = Client.objects.filter(company=request.user.company).values(
        'id', 'name', 'email', 'company'
    )
    return JsonResponse(list(clients), safe=False)


@login_required
@require_http_methods(["GET"])
def api_dashboard_stats_view(request):
    """API endpoint for dashboard statistics"""
    company = request.user.company
    
    stats = {
        'total_invoices': Invoice.objects.filter(company=company).count(),
        'total_quotes': Quote.objects.filter(company=company).count(),
        'total_receipts': Receipt.objects.filter(company=company).count(),
        'total_clients': Client.objects.filter(company=company).count(),
        'pending_invoices': Invoice.objects.filter(company=company, status='draft').count(),
        'overdue_invoices': Invoice.objects.filter(
            company=company, 
            status='sent', 
            due_date__lt=timezone.now().date()
        ).count(),
    }
    
    return JsonResponse(stats)


# Error Handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'billingapp/404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'billingapp/500.html', status=500)
