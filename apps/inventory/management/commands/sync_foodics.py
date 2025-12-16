# apps/inventory/management/commands/sync_foodics.py
from django.core.management.base import BaseCommand
from apps.inventory.services import FoodicsService

class Command(BaseCommand):
    help = 'Sync inventory data from Foodics (or Mock)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting synchronization...")
        
        service = FoodicsService()
        result = service.sync_data()
        
        self.stdout.write(self.style.SUCCESS(result))