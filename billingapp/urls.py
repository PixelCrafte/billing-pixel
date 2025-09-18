from django.urls import path
from . import views

app_name = 'billingapp'

urlpatterns = [
    # Health Check
    path('health/', views.health_check, name='health_check'),
    
    # Authentication URLs
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard and Setup
    path('home/', views.home_view, name='home'),
    path('company-setup/', views.company_setup_view, name='company_setup'),
    
    # Client Management
    path('clients/', views.ClientListView.as_view(), name='clients'),
    path('clients/add/', views.client_create_view, name='client_create'),
    path('clients/<int:client_id>/edit/', views.client_edit_view, name='client_edit'),
    path('clients/<int:client_id>/delete/', views.client_delete_view, name='client_delete'),
    
    # Invoice Management
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
    path('invoices/create/', views.invoice_create_view, name='invoice_create'),
    path('invoices/<int:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),
    path('invoices/<int:invoice_id>/edit/', views.invoice_edit_view, name='invoice_edit'),
    
    # Quote Management
    path('quotes/', views.QuoteListView.as_view(), name='quotes'),
    path('quotes/create/', views.quote_create_view, name='quote_create'),
    path('quotes/<int:quote_id>/', views.quote_detail_view, name='quote_detail'),
    
    # Receipt Management
    path('receipts/', views.ReceiptListView.as_view(), name='receipts'),
    path('receipts/create/', views.receipt_create_view, name='receipt_create'),
    path('receipts/<int:receipt_id>/', views.receipt_detail_view, name='receipt_detail'),
    
    # PDF Generation
    path('pdf/<str:document_type>/<int:document_id>/', views.generate_pdf_view, name='generate_pdf'),
    path('download/<str:token>/', views.download_pdf_view, name='download_pdf'),
    
    # Profile and Settings
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # API Endpoints
    path('api/clients/', views.api_clients_view, name='api_clients'),
    path('api/dashboard-stats/', views.api_dashboard_stats_view, name='api_dashboard_stats'),
    
    # Legacy URLs for backward compatibility
    path('clientele/', views.ClientListView.as_view(), name='clientele'),
    path('invoice/', views.invoice_create_view, name='invoice'),
    path('quotation/', views.quote_create_view, name='quotation'),
    path('receipt/', views.receipt_create_view, name='receipt'),
    path('signup/', views.register_view, name='signup'),
    path('forgot-password/', views.login_view, name='forgot_password'),  # Redirect to login for now
]