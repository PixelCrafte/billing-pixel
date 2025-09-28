import os
from billingapp.utils.pdf_generator import generate_quotation, generate_invoice, generate_receipt

def run_test():
    print("--- Starting PDF Generation Test ---")

    # --- 1. Define Sample Data and Theme ---
    # This mimics the data structure you'd get from your database
    document_details = {
        'document_title': 'Quotation',
        'document_type': 'Quotation',
        'document_number': 'Q-2024-001',
        'client_section_title': 'QUOTATION FOR',
        'document_fields': [
            {'label': 'Date', 'value': '2024-07-30'},
            {'label': 'Expires on', 'value': '2024-08-30'},
        ],
        'company': {
            'name': 'PixelCrafte Inc.',
            'tagline': 'Digital Dreams, Crafted.',
            'email': 'contact@pixelcrafte.com',
            'website': 'www.pixelcrafte.com',
        },
        'client': {
            'name': 'John Doe Corp',
            'email': 'john.doe@example.com',
            'address': '123 Innovation Drive\nTech City, TX 75001',
        },
        'items': [
            {'description': 'Website Design & Development', 'quantity': 1, 'rate': 2500.00, 'amount': 2500.00},
            {'description': 'Content Management System (CMS)', 'quantity': 1, 'rate': 800.00, 'amount': 800.00},
            {'description': 'Monthly SEO Service', 'quantity': 3, 'rate': 150.00, 'amount': 450.00},
        ],
        'totals': [
            {'label': 'Subtotal', 'value': 'R3,750.00'},
            {'label': 'VAT (15%)', 'value': 'R562.50'},
        ],
        'final_total': {
            'label': 'Total',
            'value': 'R4,312.50'
        },
        'notes': 'This quotation is valid for 30 days.\n50% deposit required to commence work.',
        'footer_text': 'Thank you for your business!',
        'theme': {
            'brand_color': '#4A90E2',        # A nice blue
            'brand_bg_color': '#D4E6F1',     # A light blue
            'text_color': '#333333',
            'font_family': 'Helvetica, Arial, sans-serif',
            'total_bg_color': '#4A90E2',
            'total_text_color': '#FFFFFF',
        }
    }

    # --- 2. Define Output Path ---
    # Create a 'test_pdfs' directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), 'test_pdfs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    quotation_path = os.path.join(output_dir, 'test_quotation.pdf')

    # --- 3. Generate the PDF ---
    print(f"Attempting to generate PDF at: {quotation_path}")
    try:
        # Call the generator function
        generate_quotation(document_details, quotation_path)

        # --- 4. Verify the Result ---
        if os.path.exists(quotation_path):
            print(f"\n[SUCCESS] PDF generated successfully!")
            print(f"You can view it here: {quotation_path}")
        else:
            print("\n[FAILURE] PDF file was not created.")

    except Exception as e:
        print(f"\n[ERROR] An exception occurred during PDF generation: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- PDF Generation Test Finished ---")

if __name__ == '__main__':
    # This allows running the test directly from the command line
    # Make sure your virtual environment is activated and you are in the project root
    # Command: python test_pdf.py
    run_test()
