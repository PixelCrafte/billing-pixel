import os
from billingapp.utils.pdf_generator import generate_quotation

def run_test_with_logo():
    print("--- Starting PDF Generation Test with Logo ---")

    # --- 1. Define Sample Data and Theme ---
    # Get the absolute path for the logo
    # The test script is in the root, so we construct the path relative to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(project_root, 'billingapp', 'static', 'billingapp', 'images', 'logo.svg')


    document_details = {
        'document_title': 'Quotation',
        'document_type': 'Quotation',
        'document_number': 'Q-2024-002',
        'client_section_title': 'QUOTATION FOR',
        'document_fields': [
            {'label': 'Date', 'value': '2025-09-28'},
            {'label': 'Expires on', 'value': '2025-10-28'},
        ],
        'company': {
            'name': 'PixelCrafte Inc.',
            'tagline': 'Digital Dreams, Crafted.',
            'email': 'contact@pixelcrafte.com',
            'website': 'www.pixelcrafte.com',
            'logo_path': f'file://{logo_path}' # WeasyPrint requires a file URI
        },
        'client': {
            'name': 'Creative Solutions LLC',
            'email': 'contact@creativesolutions.com',
            'address': '456 Design Avenue\nArt City, AC 54321',
        },
        'items': [
            {'description': 'Corporate Branding Package', 'quantity': 1, 'rate': 3500.00, 'amount': 3500.00},
            {'description': 'Social Media Kit', 'quantity': 1, 'rate': 750.00, 'amount': 750.00},
        ],
        'totals': [
            {'label': 'Subtotal', 'value': 'R 4,250.00'},
            {'label': 'VAT (15%)', 'value': 'R 637.50'},
        ],
        'final_total': {
            'label': 'Total',
            'value': 'R 4,887.50'
        },
        'notes': 'Thank you for considering PixelCrafte for your branding needs.',
        'footer_text': 'Let\'s create something amazing together!',
        'theme': {
            'brand_color': '#522CCB',        # The new color you requested
            'brand_bg_color': '#EAE6F9',     # A light purple complementary color
            'text_color': '#333333',
            'font_family': 'Helvetica, Arial, sans-serif',
            'total_bg_color': '#522CCB',
            'total_text_color': '#FFFFFF',
        }
    }

    # --- 2. Define Output Path ---
    output_dir = os.path.join(os.path.dirname(__file__), 'test_pdfs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    quotation_path = os.path.join(output_dir, 'test_quotation_with_logo.pdf')

    # --- 3. Generate the PDF ---
    print(f"Attempting to generate PDF at: {quotation_path}")
    try:
        generate_quotation(document_details, quotation_path)

        # --- 4. Verify the Result ---
        if os.path.exists(quotation_path):
            print(f"\n[SUCCESS] PDF with logo generated successfully!")
            print(f"You can view it here: {quotation_path}")
        else:
            print("\n[FAILURE] PDF file was not created.")

    except Exception as e:
        print(f"\n[ERROR] An exception occurred during PDF generation: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- PDF Generation Test Finished ---")

if __name__ == '__main__':
    run_test_with_logo()
