from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login
from .models import *
from .forms import SignUpForm
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

class HomeView(View):
    def get(self, request):
        return render(request, "billingapp/home.html")
    
class ProfileView(View):
    def get(self, request):
        return render(request, "billingapp/profile.html")

class QuotationView(View):
    def get(self, request):
        return render(request, "billingapp/quotation.html")

class QuotesView(View):
    def get(self, request):
        # In a real implementation, you'd query the database for quotes
        context = {
            'total_quotes': 15,
            'total_value': '12450.00',
            'accepted_quotes': 8,
            'conversion_rate': 53,
            'month_quotes': 3,
            'current_month': 'September',
            'current_year': '2025',
        }
        return render(request, "billingapp/quotes.html", context)
    
class InvoiceView(View):
    def get(self, request):
        return render(request, "billingapp/invoice.html")

class InvoicesView(View):
    def get(self, request):
        # In a real implementation, you'd query the database for invoices
        context = {
            'total_invoices': 12,
            'total_value': '8750.00',
            'paid_invoices': 9,
            'payment_rate': 75,
            'month_invoices': 2,
            'current_month': 'September',
            'current_year': '2025',
        }
        return render(request, "billingapp/invoices.html", context)
    
class ReceiptView(View):
    def get(self, request):
        return render(request, "billingapp/receipt.html")

class ReceiptsView(View):
    def get(self, request):
        # In a real implementation, you'd query the database for receipts
        context = {
            'total_receipts': 9,
            'total_value': '8750.00',
            'month_receipts': 2,
            'current_month': 'September',
            'current_year': '2025',
        }
        return render(request, "billingapp/receipts.html", context)

class LoginView(View):
    def get(self, request):
        return render(request, "billingapp/login.html")

class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, "billingapp/signup.html", {'form': form})
    
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after signup
            login(request, user)
            
            # Success message
            messages.success(request, f'Welcome to Billing Pixel, {user.first_name}! Your account has been created successfully.')
            
            # Check if company was created
            if hasattr(user, 'company'):
                messages.info(request, f'Your company "{user.company.name}" has been set up. You can update company details in your profile.')
            
            # Redirect to home or dashboard
            return redirect('billingapp:home')
        else:
            # Form has errors, re-render with errors
            return render(request, "billingapp/signup.html", {'form': form})


class ForgotPasswordView(View):
    def get(self, request):
        return render(request, "billingapp/forgot-password.html")
    
    def post(self, request):
        # For now, just render the template with a success message
        # In a real implementation, you'd send an email here
        email = request.POST.get('email')
        if email:
            messages.success(request, f'If an account with {email} exists, we\'ve sent a password reset link.')
        return render(request, "billingapp/forgot-password.html")


class ChangePasswordView(View):
    def get(self, request):
        return render(request, "billingapp/change-password.html")
    
    def post(self, request):
        # For now, just render the template with a success message
        # In a real implementation, you'd validate and change the password
        messages.success(request, 'Your password has been changed successfully!')
        return render(request, "billingapp/change-password.html")


class ClienteleView(View):
    def get(self, request):
        # In a real implementation, you'd query the database for clients
        context = {
            'total_clients': 48,
            'active_clients': 42,
            'new_clients': 6,
            'total_revenue': '287,450.00',
            'current_month': 'September',
            'current_year': '2025',
        }
        return render(request, "billingapp/clientele.html", context)
    