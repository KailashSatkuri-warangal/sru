from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Ticket, Asset, TicketComment


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "title",
            "category",
            "description",
            "urgency",
            "screenshot",
            "customer_name",
            "customer_phone",
            "customer_email",
            "customer_alternate_phone",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "urgency": forms.Select(attrs={"class": "form-select"}),
            "screenshot": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
            "customer_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter customer name"}
            ),
            "customer_phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., +1-234-567-8900"}
            ),
            "customer_email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "customer@example.com"}
            ),
            "customer_alternate_phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Optional alternate phone"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make customer fields required
        self.fields["customer_name"].required = True
        self.fields["customer_phone"].required = True
        self.fields["customer_email"].required = True


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["status", "urgency", "resolution_notes", "assigned_to"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "urgency": forms.Select(attrs={"class": "form-select"}),
            "resolution_notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "device_type",
            "brand",
            "serial_number",
            "purchase_date",
            "warranty_expiry",
            "status",
            "assigned_to",
        ]
        widgets = {
            "device_type": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "serial_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "purchase_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "warranty_expiry": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
        }


class AssetAssignForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ["assigned_to", "status"]
        widgets = {
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add a comment or update...",
                }
            ),
        }

