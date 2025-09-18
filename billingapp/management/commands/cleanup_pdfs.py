from django.core.management.base import BaseCommand
from django.utils import timezone
from billingapp.models import PDFLog
from billingapp.utils import cleanup_expired_pdfs
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command to clean up expired PDF files.
    Should be run periodically via cron job or task scheduler.
    """
    help = 'Clean up expired PDF files and database entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to keep PDF files (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(f"Looking for PDF files older than {days} days...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No files will be deleted"))
        
        # Get expired PDFs
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        expired_pdfs = PDFLog.objects.filter(created_at__lt=cutoff_date)
        
        total_count = expired_pdfs.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("No expired PDF files found."))
            return
        
        self.stdout.write(f"Found {total_count} expired PDF entries.")
        
        if not dry_run:
            # Actually clean up the files
            deleted_count = cleanup_expired_pdfs(days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully cleaned up {deleted_count} expired PDF files."
                )
            )
            
            # Log the cleanup
            logger.info(f"PDF cleanup completed: {deleted_count} files removed")
        else:
            # Just show what would be deleted
            for pdf_log in expired_pdfs[:10]:  # Show first 10
                self.stdout.write(f"  Would delete: {pdf_log.file_path}")
            
            if total_count > 10:
                self.stdout.write(f"  ... and {total_count - 10} more files")
            
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would delete {total_count} PDF files"
                )
            )
