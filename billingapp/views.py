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
    
class InvoiceView(View):
    def get(self, request):
        return render(request, "billingapp/invoice.html")
    
class ReceiptView(View):
    def get(self, request):
        return render(request, "billingapp/receipt.html")

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
    