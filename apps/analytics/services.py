# apps/analytics/services.py
from datetime import date, timedelta
from apps.inventory.models import StockItem
from apps.analytics.models import WasteReport

class AIEngine:
    def analyze_and_generate_report(self, branch):
        """
        يقوم بتحليل مخزون الفرع ويكتشف المخاطر وينشئ تقرير هدر
        """
        # 1. جلب المنتجات التي ستنتهي قريباً (خلال 30 يوم)
        today = date.today()
        warning_date = today + timedelta(days=30)
        
        # التغيير الأول: نستخدم StockItem بدلاً من FoodicsData
        # ونستخدم select_related لجلب بيانات المنتج (الاسم و SKU) بسرعة
        risky_items = StockItem.objects.filter(
            branch=branch,
            expiry_date__lte=warning_date
        ).select_related('product')

        if not risky_items.exists():
            return None, "All good! No waste risks detected."

        # 2. محاكاة تحليل الذكاء الاصطناعي
        total_potential_loss = 0
        analysis_text = "⚠️ **AI Waste Alert**\n\n"

        for item in risky_items:
            # افتراض السعر (لاحقاً يمكن إضافته للمودل)
            estimated_cost = 15.0 
            
            # التغيير الثاني: اسم الحقل أصبح quantity بدلاً من stock_level
            loss = item.quantity * estimated_cost
            total_potential_loss += loss

            # الذكاء: يقارن المخزون بسرعة البيع
            # نتأكد أن سرعة البيع أكبر من صفر لتجنب القسمة على صفر
            if item.sales_velocity > 0:
                days_to_sell_out = item.quantity / item.sales_velocity
            else:
                days_to_sell_out = 999 # رقم كبير يعني "لن يباع أبداً"

            days_until_expiry = (item.expiry_date - today).days

            # التغيير الثالث: الوصول لاسم المنتج و SKU يتم عبر العلاقة product
            product_ref = f"{item.product.name} ({item.product.sku})"

            if days_to_sell_out > days_until_expiry:
                analysis_text += f"- **{product_ref}**: 🔴 High Risk! Expires in {days_until_expiry} days but needs {int(days_to_sell_out)} days to sell.\n"
            else:
                analysis_text += f"- **{product_ref}**: 🟡 Moderate Risk. Expires soon ({item.expiry_date}).\n"

        analysis_text += f"\n💰 **Estimated Potential Loss:** {total_potential_loss} SAR"

        # 3. حفظ التقرير في قاعدة البيانات
        report = WasteReport.objects.create(
            branch=branch,
            total_waste_value=total_potential_loss,
            ai_analysis=analysis_text
        )

        return report, "Report generated successfully."