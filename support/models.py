from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ("hardware", "Hardware"),
        ("software", "Software"),
        ("network", "Network"),
        ("other", "Other"),
    ]

    URGENCY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tickets"
    )
    # Customer Contact Details
    customer_name = models.CharField(
        max_length=200, blank=True, null=True, help_text="Customer/Contact Name"
    )
    customer_phone = models.CharField(
        max_length=20, blank=True, null=True, help_text="Primary Phone Number"
    )
    customer_email = models.EmailField(
        blank=True, null=True, help_text="Email Address"
    )
    customer_alternate_phone = models.CharField(
        max_length=20, blank=True, null=True, help_text="Alternate Phone Number (Optional)"
    )
    screenshot = models.FileField(
        upload_to="ticket_attachments/", null=True, blank=True
    )
    resolution_notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

    def get_urgency_color(self):
        """Return Bootstrap color class for urgency."""
        colors = {
            "low": "success",
            "medium": "warning",
            "high": "danger",
        }
        return colors.get(self.urgency, "secondary")

    def get_status_color(self):
        """Return Bootstrap color class for status."""
        colors = {
            "open": "danger",
            "in_progress": "warning",
            "resolved": "success",
            "closed": "secondary",
        }
        return colors.get(self.status, "secondary")


class TicketComment(models.Model):
    """Comments/updates on tickets for activity tracking."""
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on Ticket #{self.ticket.id} by {self.user.username}"


class Asset(models.Model):
    STATUS_CHOICES = [
        ("in_use", "In Use"),
        ("available", "Available"),
        ("under_repair", "Under Repair"),
    ]

    device_type = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )

    class Meta:
        ordering = ["device_type", "brand"]

    def __str__(self) -> str:
        return f"{self.device_type} - {self.brand} ({self.serial_number})"

    def is_warranty_expired(self):
        """Check if warranty has expired."""
        from django.utils import timezone
        return self.warranty_expiry < timezone.now().date()

    def days_until_warranty_expiry(self):
        """Calculate days until warranty expires."""
        from django.utils import timezone
        delta = self.warranty_expiry - timezone.now().date()
        return delta.days

