# PDF Generation Module (`pdf_generator.py`)

This document provides instructions on how to use the `pdf_generator.py` module to create professional PDF documents for quotations, invoices, and receipts.

## Overview

The module is built on `WeasyPrint` and `Jinja2`. It works by rendering an HTML template with dynamic data and then converting that HTML to a PDF. The styling of the PDF is controlled by a `theme` object, allowing for easy customization.

## Core Functions

There are three main functions available for use:

-   `generate_quotation(document_details, file_path)`
-   `generate_invoice(document_details, file_path)`
-   `generate_receipt(document_details, file_path)`

### Arguments

Each function takes two arguments:

1.  `document_details` (dict): A Python dictionary containing all the necessary data to populate the document.
2.  `file_path` (str): The absolute path where the generated PDF file should be saved (e.g., `/path/to/your/project/output/invoice-001.pdf`).

## The `document_details` Object

This dictionary is the heart of the PDF generation. It must be structured correctly with all the required keys. Below is a detailed breakdown of its structure.

```python
document_details = {
    # --- Document Metadata ---
    'document_title': 'Invoice', # The title that appears in the browser tab/PDF metadata
    'document_type': 'Invoice',  # The big heading (e.g., "INVOICE", "QUOTATION")
    'document_number': 'INV-2025-050', # The unique identifier for the document

    # --- Dynamic Section Titles ---
    'client_section_title': 'INVOICE TO', # e.g., 'QUOTATION FOR', 'RECEIPT FOR'

    # --- Document-specific Fields (Dates, etc.) ---
    'document_fields': [
        {'label': 'Invoice Date', 'value': '2025-09-28'},
        {'label': 'Due Date', 'value': '2025-10-28'},
    ],

    # --- Company Information ---
    'company': {
        'name': 'PixelCrafte Inc.',
        'tagline': 'Digital Dreams, Crafted.',
        'email': 'contact@pixelcrafte.com',
        'website': 'www.pixelcrafte.com',
        'logo_path': 'file:///path/to/your/logo.svg' # IMPORTANT: Must be a file:// URI
    },

    # --- Client Information ---
    'client': {
        'name': 'Client Corp',
        'email': 'billing@clientcorp.com',
        'address': '789 Business Rd\nCommerce City, CC 98765', # Use \n for new lines
    },

    # --- Line Items ---
    'items': [
        {'description': 'Completed Project Phase 1', 'quantity': 1, 'rate': 5000.00, 'amount': 5000.00},
        {'description': 'Additional Support Hours', 'quantity': 5, 'rate': 100.00, 'amount': 500.00},
    ],

    # --- Calculation Summary (before the final total) ---
    'totals': [
        {'label': 'Subtotal', 'value': 'R 5,500.00'},
        {'label': 'VAT (15%)', 'value': 'R 825.00'},
    ],

    # --- The Final, Emphasized Total ---
    'final_total': {
        'label': 'Amount Due', # e.g., 'Total', 'Amount Paid'
        'value': 'R 6,325.00'
    },

    # --- Optional Notes and Footer ---
    'notes': 'Payment is due within 30 days.\nLate fees may apply.',
    'footer_text': 'Thank you for your prompt payment.',

    # --- Theme Customization ---
    'theme': {
        'brand_color': '#522CCB',
        'brand_bg_color': '#EAE6F9',
        'font_family': 'Helvetica, Arial, sans-serif',
        'total_bg_color': '#522CCB',
        'total_text_color': '#FFFFFF',
    }
}
```

### The `theme` Object

You can customize the appearance of the PDF by providing different values in the `theme` dictionary.

-   `brand_color`: The main color used for headings, table headers, and the total amount.
-   `brand_bg_color`: A light background color used for the main table header row.
-   `font_family`: The CSS font-family stack.
-   `total_bg_color`: The background color for the final total box.
-   `total_text_color`: The text color for the final total box.

## Full Example

Here is a complete, runnable example of how to generate an invoice PDF.

```python
import os
from billingapp.utils.pdf_generator import generate_invoice

# 1. Define the data for the invoice
invoice_details = {
    'document_title': 'Invoice',
    'document_type': 'Invoice',
    'document_number': 'INV-2025-050',
    'client_section_title': 'INVOICE TO',
    'document_fields': [
        {'label': 'Invoice Date', 'value': '2025-09-28'},
        {'label': 'Due Date', 'value': '2025-10-28'},
    ],
    'company': {
        'name': 'PixelCrafte Inc.',
        'tagline': 'Digital Dreams, Crafted.',
        'email': 'contact@pixelcrafte.com',
        'website': 'www.pixelcrafte.com',
        'logo_path': f"file://{os.path.abspath('path/to/logo.svg')}"
    },
    'client': {
        'name': 'Client Corp',
        'email': 'billing@clientcorp.com',
        'address': '789 Business Rd\nCommerce City, CC 98765',
    },
    'items': [
        {'description': 'Completed Project Phase 1', 'quantity': 1, 'rate': 5000.00, 'amount': 5000.00},
    ],
    'totals': [
        {'label': 'Subtotal', 'value': 'R 5,000.00'},
    ],
    'final_total': {
        'label': 'Amount Due',
        'value': 'R 5,000.00'
    },
    'notes': 'Payment is due within 30 days.',
    'footer_text': 'Thank you for your business!',
    'theme': {
        'brand_color': '#522CCB',
        'brand_bg_color': '#EAE6F9',
        'font_family': 'Helvetica, Arial, sans-serif',
        'total_bg_color': '#522CCB',
        'total_text_color': '#FFFFFF',
    }
}

# 2. Define the output path
output_directory = 'generated_pdfs'
os.makedirs(output_directory, exist_ok=True)
pdf_path = os.path.join(output_directory, 'invoice-050.pdf')

# 3. Generate the PDF
success = generate_invoice(invoice_details, pdf_path)

if success:
    print(f"Successfully generated invoice at: {pdf_path}")
else:
    print("Failed to generate invoice.")

```
