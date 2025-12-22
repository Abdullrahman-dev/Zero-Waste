from datetime import date
from apps.inventory.models import StockItem
from apps.core.models import Branch

def get_branch_context(branch_id):
    try:
        branch = Branch.objects.get(id=branch_id)
        stock_items = StockItem.objects.filter(branch=branch)
        
        inventory_list = []
        current_date = date.today()
        
        for item in stock_items:
            days_remaining = (item.expiry_date - current_date).days
            
            inventory_list.append({
                "product": item.product.name,
                "category": item.product.get_category_display() if item.product.category else "Other",
                "quantity": item.quantity,
                "unit": item.product.unit,
                "cost_price": float(item.product.cost_price or 0),
                "expiry_date": str(item.expiry_date),
                "days_remaining": days_remaining,
                "sales_velocity": item.sales_velocity
            })
        
        return {
            "branch_name": branch.name,
            "report_date": str(current_date),
            "inventory_snapshot": inventory_list
        }
        
    except Branch.DoesNotExist:
        return {}
