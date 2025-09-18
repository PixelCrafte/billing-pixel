"""
PDF generation utilities using WeasyPrint
"""
import os
import logging
from datetime import timedelta
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from .models import PDFLog, Invoice, Quote, Receipt

logger = logging.getLogger(__name__)

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint not installed. PDF generation will be disabled.")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_pdf_from_html(html_content, css_content=None):
    """
    Generate PDF from HTML content using WeasyPrint or ReportLab fallback
    """
    if not WEASYPRINT_AVAILABLE and not REPORTLAB_AVAILABLE:
        raise ValueError("Neither WeasyPrint nor ReportLab is available for PDF generation")
    
    if WEASYPRINT_AVAILABLE:
        try:
            # Use WeasyPrint (preferred)
            html_doc = weasyprint.HTML(string=html_content)
            
            css_docs = []
            if css_content:
                css_docs.append(weasyprint.CSS(string=css_content))
            
            pdf_bytes = html_doc.write_pdf(stylesheets=css_docs)
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"WeasyPrint PDF generation failed: {e}")
            if not REPORTLAB_AVAILABLE:
                raise
    
    if REPORTLAB_AVAILABLE:
        # Fallback to ReportLab (basic PDF generation)
        logger.info("Using ReportLab fallback for PDF generation")
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Very basic text extraction from HTML (for fallback only)
        import re
        text_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Write text to PDF (basic implementation)
        lines = text_content.split('\n')
        y_position = 750
        
        for line in lines[:40]:  # Limit to first 40 lines
            if y_position < 50:
                p.showPage()
                y_position = 750
            p.drawString(50, y_position, line.strip())
            y_position -= 20
        
        p.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    raise ValueError("No PDF generation library available")


def create_pdf_for_document(document, document_type):
    """
    Create PDF for invoice, quote, or receipt
    Returns PDFLog instance with download token
    """
    if not document.versioned_data:
        document.lock_version_data()
    
    # Render HTML template
    template_name = f'billingapp/pdf/{document_type}_pdf.html'
    context = {
        'document': document,
        'versioned_data': document.versioned_data,
        'company': document.company,
    }
    
    html_content = render_to_string(template_name, context)
    
    # Generate CSS with company theming
    css_content = generate_themed_css(document.company)
    
    # Generate PDF
    pdf_bytes = generate_pdf_from_html(html_content, css_content)
    
    # Save to temporary file
    expires_at = timezone.now() + timedelta(seconds=settings.PDF_DOWNLOAD_EXPIRES_SECONDS)
    
    pdf_log = PDFLog.objects.create(
        company=document.company,
        document_type=document_type,
        document_id=document.id,
        expires_at=expires_at,
    )
    
    # Create file path
    filename = f"{document_type}_{document.number}_{pdf_log.download_token[:8]}.pdf"
    file_path = settings.PDF_TEMP_STORAGE_PATH / filename
    
    # Write PDF to file
    with open(file_path, 'wb') as f:
        f.write(pdf_bytes)
    
    pdf_log.file_path = str(file_path)
    pdf_log.save(update_fields=['file_path'])
    
    return pdf_log


def generate_themed_css(company):
    """
    Generate CSS with company branding variables
    """
    css_template = """
    :root {
        --primary-r: %(primary_r)s;
        --primary-g: %(primary_g)s;
        --primary-b: %(primary_b)s;
        --accent-r: %(accent_r)s;
        --accent-g: %(accent_g)s;
        --accent-b: %(accent_b)s;
        --font-family: %(font_family)s;
    }
    
    body {
        font-family: var(--font-family);
        margin: 0;
        padding: 20px;
        line-height: 1.6;
        color: #333;
    }
    
    .header {
        border-bottom: 3px solid rgb(var(--primary-r), var(--primary-g), var(--primary-b));
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    
    .company-logo {
        max-height: 60px;
        margin-bottom: 10px;
    }
    
    .company-name {
        font-size: 24px;
        font-weight: bold;
        color: rgb(var(--primary-r), var(--primary-g), var(--primary-b));
        margin: 0;
    }
    
    .document-title {
        font-size: 32px;
        font-weight: bold;
        color: rgb(var(--primary-r), var(--primary-g), var(--primary-b));
        text-align: right;
        margin: 0;
    }
    
    .document-number {
        font-size: 18px;
        color: rgb(var(--accent-r), var(--accent-g), var(--accent-b));
        text-align: right;
        margin: 5px 0;
    }
    
    .client-info {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    
    .items-table {
        width: 100%%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    
    .items-table th {
        background-color: rgb(var(--primary-r), var(--primary-g), var(--primary-b));
        color: white;
        padding: 12px;
        text-align: left;
    }
    
    .items-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #ddd;
    }
    
    .items-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    .totals-section {
        margin-top: 30px;
        text-align: right;
    }
    
    .total-row {
        margin: 5px 0;
        font-size: 16px;
    }
    
    .final-total {
        font-size: 20px;
        font-weight: bold;
        color: rgb(var(--primary-r), var(--primary-g), var(--primary-b));
        border-top: 2px solid rgb(var(--primary-r), var(--primary-g), var(--primary-b));
        padding-top: 10px;
        margin-top: 10px;
    }
    
    .footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        font-size: 12px;
        color: #666;
    }
    
    @page {
        margin: 2cm;
    }
    """
    
    primary_r, primary_g, primary_b = company.get_rgb_primary()
    accent_r, accent_g, accent_b = company.get_rgb_accent()
    
    return css_template % {
        'primary_r': primary_r,
        'primary_g': primary_g,
        'primary_b': primary_b,
        'accent_r': accent_r,
        'accent_g': accent_g,
        'accent_b': accent_b,
        'font_family': company.font_family,
    }


def serve_pdf_download(request, token):
    """
    Serve PDF file for download using secure token
    """
    try:
        pdf_log = get_object_or_404(PDFLog, download_token=token)
        
        # Check if expired
        if pdf_log.is_expired:
            raise Http404("Download link has expired")
        
        # Check if file exists
        if not pdf_log.file_path or not os.path.exists(pdf_log.file_path):
            raise Http404("PDF file not found")
        
        # Mark as downloaded
        if not pdf_log.downloaded_at:
            pdf_log.downloaded_at = timezone.now()
            pdf_log.save(update_fields=['downloaded_at'])
        
        # Serve file
        with open(pdf_log.file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            
        filename = f"{pdf_log.document_type}_{pdf_log.document_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"PDF download error: {e}")
        raise Http404("PDF download failed")


def cleanup_expired_pdfs(days=7):
    """
    Clean up expired PDF files - run as management command or Celery task
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    expired_logs = PDFLog.objects.filter(
        created_at__lt=cutoff_date,
        deleted=False
    )
    
    cleaned_count = 0
    
    for log in expired_logs:
        try:
            if log.file_path and os.path.exists(log.file_path):
                os.remove(log.file_path)
                logger.info(f"Deleted expired PDF: {log.file_path}")
            
            log.deleted = True
            log.file_path = None
            log.save(update_fields=['deleted', 'file_path'])
            cleaned_count += 1
            
        except Exception as e:
            logger.error(f"Error cleaning up PDF {log.id}: {e}")
    
    logger.info(f"Cleaned up {cleaned_count} expired PDF files")
    return cleaned_count


def generate_next_number(company, document_type):
    """
    Generate the next document number for a company.
    
    Args:
        company: Company instance
        document_type: 'invoice', 'quote', or 'receipt'
        
    Returns:
        Next formatted document number
    """
    from .models import Invoice, Quote, Receipt
    
    model_map = {
        'invoice': (Invoice, company.invoice_prefix or 'INV-'),
        'quote': (Quote, company.quote_prefix or 'QUO-'),
        'receipt': (Receipt, company.receipt_prefix or 'REC-')
    }
    
    if document_type not in model_map:
        raise ValueError(f"Invalid document type: {document_type}")
    
    model, prefix = model_map[document_type]
    
    # Get the latest number for this company and document type
    latest_doc = model.objects.filter(
        company=company,
        number__startswith=prefix
    ).order_by('-created_at').first()
    
    if latest_doc:
        # Extract the numeric part and increment
        try:
            current_number = int(latest_doc.number.replace(prefix, ''))
            next_number = current_number + 1
        except ValueError:
            # If we can't parse the number, start from 1
            next_number = 1
    else:
        next_number = 1
    
    return f"{prefix}{next_number:04d}"
