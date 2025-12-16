# apps/operations/models.py
from django.db import models
from django.conf import settings
from apps.core.models import Branch

class OperationalRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='operational_requests'
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True) 
    
    type = models.CharField(max_length=100)
    details = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=RequestStatus.choices, 
        default=RequestStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

class SupportTicket(models.Model):
    class TicketStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        CLOSED = 'CLOSED', 'Closed'

    class Priority(models.IntegerChoices):
        LOW = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH = 3, 'High'

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.OPEN)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    
    created_at = models.DateTimeField(auto_now_add=True)