"""
PDF Generation Module for PixelCrafte Billing System using WeasyPrint

This module provides functions to generate professional, themeable PDF documents 
for quotations, invoices, and receipts by converting dynamic HTML content.
"""

import os
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

def _generate_css(theme):
    """Generates dynamic CSS from a theme object."""
    brand_color = theme.get('brand_color', '#4A90E2')
    brand_bg_color = theme.get('brand_bg_color', '#D4E6F1')
    font_family = theme.get('font_family', "'Helvetica', 'Arial', sans-serif")
    total_bg_color = theme.get('total_bg_color', '#4A90E2')
    total_text_color = theme.get('total_text_color', '#FFFFFF')

    return f"""
    @page {{
        size: letter;
        margin: 0.75in;
    }}
    body {{
        font-family: {font_family};
        color: #333;
        font-size: 10pt;
    }}
    .header, .footer {{
        color: #777;
    }}
    .brand-color {{
        color: {brand_color};
    }}
    .brand-bg {{
        background-color: {brand_bg_color};
        /* A text color that works on the light background */
        color: #333; 
    }}
    .table th {{
        background-color: {brand_color};
        color: white;
    }}
    .total-line {{
        background-color: #f4f4f5;
    }}
    .total-line.brand-total {{
        background-color: {total_bg_color};
    }}
    .total-amount {{
        color: {total_text_color};
        font-weight: bold;
    }}
    """

def _render_html(template_name, document_details):
    """Renders an HTML template with the given document details."""
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=FileSystemLoader(template_dir))
    
    def currency_format(value):
        if isinstance(value, (int, float)):
            return f"R{value:,.2f}".replace(",", " ")
        return value
    env.filters['currency'] = currency_format

    template = env.get_template(template_name)
    return template.render(data=document_details)

def _render_html(template_name, document_details):
    """Renders an HTML template with the given document details."""
    # Set up Jinja2 environment
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Add a format filter for currency
    def currency_format(value):
        # Format as R currency, with spaces for thousands separators
        return f"R{value:,.2f}".replace(",", " ")
    env.filters['currency'] = currency_format

    template = env.get_template(template_name)
    return template.render(data=document_details)

def _create_pdf(document_details, file_path, template_name):
    """
    Core function to create a PDF from document details and a template.
    
    Args:
        document_details (dict): The dictionary containing all data for the document.
        file_path (str): The absolute path where the PDF will be saved.
        template_name (str): The name of the HTML template to use.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Get theme from details, or use a default
        theme = document_details.get('theme', {})
        
        # Render HTML from template
        html_content = _render_html(template_name, document_details)
        
        # Generate dynamic CSS
        dynamic_css = _generate_css(theme)
        
        # Create WeasyPrint objects
        html = HTML(string=html_content)
        css = CSS(string=dynamic_css)
        
        # Write PDF
        html.write_pdf(file_path, stylesheets=[css])
        
        print(f"Successfully generated PDF: {file_path}")
        return True
        
    except Exception as e:
        import traceback
        print(f"Error generating PDF: {e}")
        traceback.print_exc()
        return False

def generate_quotation(document_details, file_path):
    """
    Generates a quotation PDF.
    
    Args:
        document_details (dict): Data for the quotation, including a 'theme' key.
        file_path (str): Path to save the PDF.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    return _create_pdf(document_details, file_path, 'quotation_template.html')

def generate_invoice(document_details, file_path):
    """
    Generates an invoice PDF.
    
    Args:
        document_details (dict): Data for the invoice, including a 'theme' key.
        file_path (str): Path to save the PDF.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    return _create_pdf(document_details, file_path, 'invoice_template.html')

def generate_receipt(document_details, file_path):
    """
    Generates a receipt PDF.
    
    Args:
        document_details (dict): Data for the receipt, including a 'theme' key.
        file_path (str): Path to save the PDF.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    return _create_pdf(document_details, file_path, 'receipt_template.html')
