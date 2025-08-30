from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()

class SignUpForm(UserCreationForm):
    """
    Custom signup form that extends Django's UserCreationForm.
    Includes email field and company setup in one step.
    """
    
    # User fields
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input_field',
            'placeholder': 'your@email.com',
            'id': 'email_field'
        }),
        help_text="We'll never share your email with anyone else."
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input_field',
            'placeholder': 'John',
            'id': 'first_name_field'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input_field',
            'placeholder': 'Doe',
            'id': 'last_name_field'
        })
    )
    
    # Company fields (optional during signup)
    company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input_field',
            'placeholder': 'Your Company Name (Optional)',
            'id': 'company_name_field'
        }),
        help_text="You can set this up later in your profile."
    )
    
    # Override password fields to add custom styling
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'input_field',
            'placeholder': 'Password',
            'id': 'password_field'
        }),
        help_text="Your password must contain at least 8 characters."
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'input_field',
            'placeholder': 'Confirm Password',
            'id': 'password2_field'
        }),
        help_text="Enter the same password as before, for verification."
    )
    
    # Terms and conditions
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox_field',
            'id': 'terms_field'
        }),
        label="I agree to the Terms of Service and Privacy Policy"
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input_field',
                'placeholder': 'Username',
                'id': 'username_field'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field order
        self.fields['username'].help_text = "150 characters or fewer. Letters, digits and @/./+/-/_ only."
        
        # Remove the default help text for password fields if needed
        # self.fields['password1'].help_text = None
        
    def clean_email(self):
        """
        Validate that the email is unique.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        """
        Validate that the username is unique and meets requirements.
        """
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username
    
    def save(self, commit=True):
        """
        Save the user and optionally create a company.
        """
        # Save the user
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create a company if company_name was provided
            company_name = self.cleaned_data.get('company_name')
            if company_name:
                Company.objects.create(
                    owner=user,
                    name=company_name,
                    email=user.email,  # Use user's email as default company email
                )
        
        return user


class CompanySetupForm(forms.ModelForm):
    """
    Separate form for detailed company setup (can be used after signup).
    """
    
    class Meta:
        model = Company
        fields = [
            'name', 'registration_number', 'tax_number', 'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'default_currency', 'default_vat_rate', 'default_discount_rate'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input_field', 'placeholder': 'Company Name'}),
            'registration_number': forms.TextInput(attrs={'class': 'input_field', 'placeholder': 'Registration Number'}),
            'tax_number': forms.TextInput(attrs={'class': 'input_field', 'placeholder': 'Tax Number'}),
            'email': forms.EmailInput(attrs={'class': 'input_field', 'placeholder': 'company@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'input_field', 'placeholder': '+1 (555) 123-4567'}),
            'website': forms.URLInput(attrs={'class': 'input_field', 'placeholder': 'https://yourcompany.com'}),
            'address_line1': forms.TextInput(attrs={'class': 'input_field', 'placeholder': '123 Main Street'}),
            'address_line2': forms.TextInput(attrs={'class': 'input_field', 'placeholder': 'Suite 100'}),
            'city': forms.TextInput(attrs={'class': 'input_field', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'input_field', 'placeholder': 'State/Province'}),
            'postal_code': forms.TextInput(attrs={'class': 'input_field', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'input_field', 'placeholder': 'Country'}),
            'default_currency': forms.Select(attrs={'class': 'select_field'}),
            'default_vat_rate': forms.NumberInput(attrs={'class': 'input_field', 'placeholder': '0.00', 'step': '0.01'}),
            'default_discount_rate': forms.NumberInput(attrs={'class': 'input_field', 'placeholder': '0.00', 'step': '0.01'}),
        }
