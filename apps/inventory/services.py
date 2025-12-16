# apps/inventory/services.py
import random
from datetime import date, timedelta
from django.conf import settings
from .models import FoodicsData, Branch

class FoodicsService:
    def sync_data(self):
        """
        الدالة الرئيسية التي تستدعيها الواجهة أو النظام
        """
        if settings.USE_MOCK_API:
            print("⚠️ Using MOCK data for simulation...")
            return self._generate_mock_data()
        else:
            print("🔌 Connecting to Real Foodics API...")
            return self._fetch_real_api_data()

    def _generate_mock_data(self):
        """
        توليد بيانات وهمية ذكية للمحاكاة
        """
        branches = Branch.objects.all()
        if not branches.exists():
            return "No branches found! Please create a branch first."

        mock_products = [
            {"sku": "BURGER-001", "name": "Beef Burger"},
            {"sku": "CHEESE-002", "name": "Cheddar Cheese"},
            {"sku": "BUN-003", "name": "Burger Bun"},
            {"sku": "TOMATO-004", "name": "Fresh Tomato"},
        ]

        created_count = 0

        for branch in branches:
            for prod in mock_products:
                # محاكاة بيانات متغيرة (عشان الديمو يكون حيوي)
                FoodicsData.objects.update_or_create(
                    branch=branch,
                    sku=prod["sku"],
                    batch_id=f"BATCH-{random.randint(1000, 9999)}",
                    defaults={
                        "expiry_date": date.today() + timedelta(days=random.randint(1, 30)),
                        "stock_level": random.randint(5, 500), # رقم عشوائي للمخزون
                        "sales_velocity": round(random.uniform(0.5, 5.0), 2), # سرعة بيع عشوائية
                    }
                )
                created_count += 1
        
        return f"✅ Successfully synced {created_count} items (MOCK MODE)."

    def _fetch_real_api_data(self):
        """
        هنا نكتب كود الاتصال الحقيقي مستقبلاً
        """
        # TODO: Implement actual API call using requests library
        # token = settings.FOODICS_TOKEN
        # response = requests.get('https://api.foodics.com/v5/inventory', headers=...)
        pass