from django.urls import path
from . import views

app_name = 'billingapp'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('quotation/', views.QuotationView.as_view(), name='quotation'),
    path('invoice/', views.InvoiceView.as_view(), name='invoice'),
    path('receipt/', views.ReceiptView.as_view(), name='receipt'),
]