
import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.core.models import RestaurantCompany, Branch
from apps.inventory.models import Product, StockItem, BranchStockSetting
from apps.analytics.models import WasteReport, WasteLog
from apps.operations.models import OperationalRequest
from apps.notifications.models import UserNotification

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with realistic demo data for Zero Waste Project'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('⚠️  Starting Data Seeding...'))
        
        # 1. Create Companies
        companies_data = [
            {'name': 'Maestro Pizza', 'manager': 'maestro_admin'},
            {'name': 'Al-Baik', 'manager': 'albaik_admin'},
            {'name': 'Healthy Green', 'manager': 'green_admin'},
        ]
        
        companies = []
        for c_data in companies_data:
            # FIX: Use update_or_create to fix roles if they exist
            manager_user, created = User.objects.update_or_create(
                username=c_data['manager'],
                defaults={'email': f"{c_data['manager']}@example.com", 'role': 'manager'}
            )
            if created:
                manager_user.set_password('123456')
                manager_user.save()
            
            company, _ = RestaurantCompany.objects.get_or_create(
                name=c_data['name'],
                defaults={'manager': manager_user, 'subscription_status': True}
            )
            companies.append(company)
            self.stdout.write(f"✅ Company Created: {company.name}")

        # 2. Create Branches & Products for Maestro (Example)
        maestro = companies[0]
        
        # Products
        products_data = [
            {'name': 'Mozzarella Cheese', 'category': 'dairy', 'unit': 'kg', 'cost': 35.0, 'min': 10},
            {'name': 'Pepperoni', 'category': 'meat', 'unit': 'kg', 'cost': 45.0, 'min': 5},
            {'name': 'Pizza Dough', 'category': 'bakery', 'unit': 'kg', 'cost': 5.0, 'min': 50},
            {'name': 'Tomato Sauce', 'category': 'vegetables', 'unit': 'liter', 'cost': 12.0, 'min': 20},
            {'name': 'Green Peppers', 'category': 'vegetables', 'unit': 'kg', 'cost': 7.0, 'min': 5},
            {'name': 'Olive Oil', 'category': 'spices', 'unit': 'liter', 'cost': 25.0, 'min': 5},
        ]
        
        maestro_products = []
        for p in products_data:
            prod, _ = Product.objects.get_or_create(
                name=p['name'],
                company=maestro,
                defaults={
                    'category': p['category'],
                    'unit': p['unit'],
                    'cost_price': p['cost'],
                    'minimum_quantity': p['min'],
                    'sku': f"SKU-{random.randint(1000, 9999)}"
                }
            )
            maestro_products.append(prod)

        # Branches
        branches_data = [
            {'name': 'Riyadh - Olaya', 'location': 'Olaya St.', 'manager': 'olaya_mngr'},
            {'name': 'Riyadh - Malqa', 'location': 'Malqa Dist.', 'manager': 'malqa_mngr'},
            {'name': 'Jeddah - Corniche', 'location': 'Corniche Rd.', 'manager': 'jed_mngr'},
        ]
        
        for b_data in branches_data:
            # FIX: Use update_or_create to fix roles if they exist
            b_manager, created = User.objects.update_or_create(
                username=b_data['manager'],
                defaults={'email': f"{b_data['manager']}@example.com", 'role': 'branch_manager'}
            )
            if created:
                b_manager.set_password('123456')
                b_manager.save()
                
            branch, _ = Branch.objects.get_or_create(
                name=b_data['name'],
                company=maestro,
                defaults={'location': b_data['location'], 'manager': b_manager}
            )
            
            # 3. Operations: requests
            OperationalRequest.objects.create(
                branch=branch,
                type='RESTOCK',
                status=random.choice(['PENDING', 'APPROVED', 'REJECTED']),
                submitted_by=b_manager,
                details=f"Urgent restock for weekend rush at {branch.name}"
            )

            # 4. Inventory & Stock Items
            for prod in maestro_products:
                # Random stock levels
                qty = random.uniform(2.0, 100.0)
                StockItem.objects.create(
                    branch=branch,
                    product=prod,
                    batch_id=f"BATCH-{random.randint(10000, 99999)}",
                    quantity=qty,
                    initial_quantity=qty + random.uniform(5, 20),
                    expiry_date=date.today() + timedelta(days=random.randint(-5, 60)), # Some expired
                    sales_velocity=random.uniform(0.5, 5.0)
                )

            # 5. Waste Reports (Historical Data - Last 30 Days)
            self.stdout.write(f"   Generating 30 days of waste data for {branch.name}...")
            for i in range(30):
                day = timezone.now() - timedelta(days=i)
                # Ensure date is not in future
                
                # Daily Waste Logic
                daily_waste_val = 0
                
                # Create random individual logs per day
                for _ in range(random.randint(0, 3)):
                    target_prod = random.choice(maestro_products)
                    w_qty = random.uniform(0.5, 3.0)
                    cost = float(target_prod.cost_price) * w_qty
                    daily_waste_val += cost
                    
                    log = WasteLog.objects.create(
                        branch=branch,
                        product=target_prod,
                        quantity=w_qty,
                        reason=random.choice(['expired', 'damaged', 'prepared_incorrectly']),
                        submitted_by=b_manager,
                    )
                    log.created_at = day
                    log.save()

                # Create Aggregated Report for the day
                if daily_waste_val > 0:
                    report = WasteReport.objects.create(
                        branch=branch,
                        total_waste_value=daily_waste_val,
                        ai_analysis=f'{{"performance_verdict": "Mock Analysis for {day.date()}"}}'
                    )
                    # Manually update date to past
                    report.generated_date = day
                    report.save()

            self.stdout.write(f"✅ Branch Setup Complete: {branch.name}")

        self.stdout.write(self.style.SUCCESS('🎉 Database Seeding Completed Successfully!'))
        self.stdout.write(self.style.SUCCESS('   Superuser: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('   Managers: maestro_admin / 123456'))
