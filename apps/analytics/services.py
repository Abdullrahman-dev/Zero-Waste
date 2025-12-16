# apps/analytics/services.py
from datetime import date, timedelta
import random
from apps.inventory.models import FoodicsData
from apps.analytics.models import WasteReport

class AIEngine:
    def analyze_and_generate_report(self, branch):
        """
        يقوم بتحليل مخزون الفرع ويكتشف المخاطر وينشئ تقرير هدر
        """
        # 1. جلب المنتجات التي ستنتهي قريباً (خلال 30 يوم مثلاً)
        today = date.today()
        warning_date = today + timedelta(days=30)
        
        risky_items = FoodicsData.objects.filter(
            branch=branch,
            expiry_date__lte=warning_date
        )

        if not risky_items.exists():
            return None, "All good! No waste risks detected."

        # 2. محاكاة تحليل الذكاء الاصطناعي (Logic Simulation)
        total_potential_loss = 0
        analysis_text = "⚠️ **AI Waste Alert**\n\n"

        for item in risky_items:
            # نفترض سعر افتراضي 15 ريال للكيلو/القطعة لأننا لم نضف السعر للمودل بعد
            estimated_cost = 15.0 
            loss = item.stock_level * estimated_cost
            total_potential_loss += loss

            # الذكاء: يقارن المخزون بسرعة البيع
            days_to_sell_out = item.stock_level / item.sales_velocity if item.sales_velocity > 0 else 999
            days_until_expiry = (item.expiry_date - today).days

            if days_to_sell_out > days_until_expiry:
                analysis_text += f"- **{item.sku}**: High Risk! Stock will expire in {days_until_expiry} days but needs {int(days_to_sell_out)} days to sell.\n"
            else:
                analysis_text += f"- **{item.sku}**: Moderate Risk. Expires soon ({item.expiry_date}).\n"

        analysis_text += f"\n💰 **Estimated Potential Loss:** {total_potential_loss} SAR"

        # 3. حفظ التقرير في قاعدة البيانات
        report = WasteReport.objects.create(
            branch=branch,
            total_waste_value=total_potential_loss,
            ai_analysis=analysis_text
        )

        return report, "Report generated successfully."