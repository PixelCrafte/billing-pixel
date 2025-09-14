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
    path('quotes/', views.QuotesView.as_view(), name='quotes'),
    path('invoice/', views.InvoiceView.as_view(), name='invoice'),
    path('invoices/', views.InvoicesView.as_view(), name='invoices'),
    path('receipt/', views.ReceiptView.as_view(), name='receipt'),
    path('receipts/', views.ReceiptsView.as_view(), name='receipts'),
    path('clientele/', views.ClienteleView.as_view(), name='clientele'),
]