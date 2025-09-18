from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from billingapp.models import Company, Client, Invoice, Quote, Receipt, InvoiceLineItem, QuoteLineItem
from django.utils import timezone
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to seed the database with sample data for development and testing.
    """
    help = 'Seed the database with sample data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--companies',
            type=int,
            default=3,
            help='Number of sample companies to create (default: 3)'
        )
        parser.add_argument(
            '--clients-per-company',
            type=int,
            default=5,
            help='Number of clients per company (default: 5)'
        )
        parser.add_argument(
            '--documents-per-client',
            type=int,
            default=3,
            help='Number of documents per client (default: 3)'
        )

    def handle(self, *args, **options):
        companies_count = options['companies']
        clients_per_company = options['clients_per_company']
        documents_per_client = options['documents_per_client']
        
        self.stdout.write("Starting database seeding...")
        
        # Create sample companies with users
        companies_created = 0
        for i in range(companies_count):
            company_name = f"Sample Company {i+1}"
            
            # Check if company already exists
            if Company.objects.filter(name=company_name).exists():
                self.stdout.write(f"Company '{company_name}' already exists, skipping...")
                continue
            
            # Create user for the company
            user_email = f"owner{i+1}@company{i+1}.com"
            
            if User.objects.filter(email=user_email).exists():
                user = User.objects.get(email=user_email)
            else:
                user = User.objects.create_user(
                    username=user_email,
                    email=user_email,
                    password='password123',
                    first_name=f'Owner{i+1}',
                    last_name=f'Company{i+1}',
                    role='owner'
                )
            
            # Create company
            company = Company.objects.create(
                name=company_name,
                email=user_email,
                phone=f'+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}',
                address_line1=f'{random.randint(100,9999)} Main Street',
                city='Sample City',
                state='CA',
                postal_code=f'{random.randint(10000,99999)}',
                country='United States',
                primary_color='#3B82F6',
                secondary_color='#64748B',
                currency='USD'
            )
            
            # Link user to company
            user.company = company
            user.save()
            
            companies_created += 1
            self.stdout.write(f"Created company: {company_name}")
            
            # Create clients for this company
            clients_created = 0
            for j in range(clients_per_company):
                client = Client.objects.create(
                    company=company,
                    name=f'Client {j+1}',
                    email=f'client{j+1}@company{i+1}.com',
                    phone=f'+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}',
                    company=f'Client Company {j+1}',
                    address=f'{random.randint(100,9999)} Client Street\nSample City, CA {random.randint(10000,99999)}',
                )
                clients_created += 1
                
                # Create documents for this client
                documents_created = 0
                for k in range(documents_per_client):
                    # Create invoice
                    invoice = Invoice.objects.create(
                        company=company,
                        client=client,
                        number=f'INV-{company.id:03d}-{k+1:04d}',
                        issue_date=timezone.now().date(),
                        due_date=timezone.now().date() + timezone.timedelta(days=30),
                        currency='USD',
                        tax_rate=Decimal('8.25'),
                        status='sent'
                    )
                    
                    # Add line items to invoice
                    for l in range(random.randint(1, 4)):
                        InvoiceLineItem.objects.create(
                            invoice=invoice,
                            description=f'Service {l+1}',
                            quantity=Decimal(str(random.randint(1, 10))),
                            unit_price=Decimal(str(random.randint(50, 500)))
                        )
                    
                    invoice.calculate_totals()
                    invoice.save()
                    
                    # Create quote
                    quote = Quote.objects.create(
                        company=company,
                        client=client,
                        number=f'QUO-{company.id:03d}-{k+1:04d}',
                        issue_date=timezone.now().date(),
                        valid_until=timezone.now().date() + timezone.timedelta(days=30),
                        currency='USD',
                        tax_rate=Decimal('8.25'),
                        status='sent'
                    )
                    
                    # Add line items to quote
                    for l in range(random.randint(1, 3)):
                        QuoteLineItem.objects.create(
                            quote=quote,
                            description=f'Quoted Service {l+1}',
                            quantity=Decimal(str(random.randint(1, 5))),
                            unit_price=Decimal(str(random.randint(100, 1000)))
                        )
                    
                    quote.calculate_totals()
                    quote.save()
                    
                    # Create receipt (50% chance)
                    if random.choice([True, False]):
                        Receipt.objects.create(
                            company=company,
                            client=client,
                            invoice=invoice,
                            number=f'REC-{company.id:03d}-{k+1:04d}',
                            amount=invoice.total_amount,
                            currency='USD',
                            payment_method='bank_transfer'
                        )
                    
                    documents_created += 3
                
                self.stdout.write(f"  Created client: {client.name} with {documents_created} documents")
            
            self.stdout.write(f"  Created {clients_created} clients for {company_name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {companies_created} companies with sample data!'
            )
        )
        
        # Print login instructions
        self.stdout.write("\n" + "="*50)
        self.stdout.write("LOGIN INSTRUCTIONS:")
        self.stdout.write("="*50)
        for i in range(companies_created):
            self.stdout.write(f"Company {i+1}:")
            self.stdout.write(f"  Email: owner{i+1}@company{i+1}.com")
            self.stdout.write(f"  Password: password123")
            self.stdout.write("")
        
        self.stdout.write("You can now log in with any of the above credentials to test the system.")
