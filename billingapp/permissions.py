"""
Role-based permissions for multi-tenant billing system
"""
from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import User


def require_company_permission(permission_type):
    """
    Decorator to check if user has permission for company operations
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            if not hasattr(request.user, 'company') or not request.user.company:
                raise PermissionDenied("No company associated with user")
            
            if not request.user.has_company_permission(permission_type):
                raise PermissionDenied(f"Insufficient permissions for {permission_type}")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_company_owner(view_func):
    """
    Decorator to require company owner role
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        if request.user.role != User.Role.OWNER:
            raise PermissionDenied("Owner role required")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def require_company_admin(view_func):
    """
    Decorator to require company admin or owner role
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        if request.user.role not in [User.Role.OWNER, User.Role.ADMIN]:
            raise PermissionDenied("Admin role required")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class CompanyPermissionMixin:
    """
    Mixin for class-based views to check company permissions
    """
    required_permissions = []  # List of required permissions
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        if not hasattr(request.user, 'company') or not request.user.company:
            raise PermissionDenied("No company associated with user")
        
        # Check if user has any of the required permissions
        if self.required_permissions:
            has_permission = False
            for permission in self.required_permissions:
                if request.user.has_company_permission(permission):
                    has_permission = True
                    break
            
            if not has_permission:
                raise PermissionDenied(f"Insufficient permissions. Required: {self.required_permissions}")
        
        return super().dispatch(request, *args, **kwargs)


class CompanyOwnerMixin:
    """
    Mixin for class-based views to require company owner
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        if request.user.role != User.Role.OWNER:
            raise PermissionDenied("Owner role required")
        
        return super().dispatch(request, *args, **kwargs)


def filter_by_company(queryset, user):
    """
    Filter queryset by user's company for multi-tenant isolation
    """
    if not user.is_authenticated or not hasattr(user, 'company') or not user.company:
        return queryset.none()
    
    return queryset.filter(company=user.company)


def can_user_access_document(user, document):
    """
    Check if user can access a specific document
    """
    if not user.is_authenticated:
        return False
    
    if not hasattr(user, 'company') or not user.company:
        return False
    
    # Check if document belongs to user's company
    if document.company != user.company:
        return False
    
    # Owners and admins can access all documents
    if user.role in [User.Role.OWNER, User.Role.ADMIN]:
        return True
    
    # Accountants can access all invoices and receipts
    if user.role == User.Role.ACCOUNTANT:
        return True
    
    # Regular users can only access documents they created
    if hasattr(document, 'created_by') and document.created_by == user:
        return True
    
    return False


def can_user_edit_document(user, document):
    """
    Check if user can edit a specific document
    """
    if not can_user_access_document(user, document):
        return False
    
    # Can't edit sent/paid documents unless admin/owner
    if document.status in ['sent', 'paid', 'partially_paid'] and user.role not in [User.Role.OWNER, User.Role.ADMIN]:
        return False
    
    return True


def can_user_delete_document(user, document):
    """
    Check if user can delete a specific document
    """
    if not can_user_access_document(user, document):
        return False
    
    # Only owners and admins can delete
    if user.role not in [User.Role.OWNER, User.Role.ADMIN]:
        return False
    
    # Can't delete paid documents
    if document.status in ['paid', 'partially_paid']:
        return False
    
    return True


# Aliases for backward compatibility with views.py
def can_view_document(user, document):
    """Alias for can_user_access_document"""
    return can_user_access_document(user, document)


def can_edit_document(user, document):
    """Alias for can_user_edit_document"""
    return can_user_edit_document(user, document)


def can_delete_document(user, document):
    """Alias for can_user_delete_document"""
    return can_user_delete_document(user, document)
