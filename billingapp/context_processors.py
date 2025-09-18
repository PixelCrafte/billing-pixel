from django.conf import settings
from .models import Company


def company_context(request):
    """Add company context to all templates"""
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'company') and request.user.company:
        context['user_company'] = request.user.company
    
    return context


def theme_context(request):
    """Add theming context for CSS variables"""
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'company') and request.user.company:
        company = request.user.company
        context.update({
            'primary_rgb': company.get_primary_rgb_string(),
            'accent_rgb': company.get_accent_rgb_string(),
            'company_font_family': company.font_family,
            'company_primary_color': company.primary_color,
            'company_accent_color': company.accent_color,
        })
    else:
        # Default theme values
        context.update({
            'primary_rgb': '107, 70, 193',  # #6B46C1
            'accent_rgb': '139, 92, 246',   # #8B5CF6
            'company_font_family': 'Inter, system-ui, sans-serif',
            'company_primary_color': '#6B46C1',
            'company_accent_color': '#8B5CF6',
        })
    
    return context
