from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.contrib import messages
import csv
from datetime import datetime, timedelta

from .forms import (
    LoginForm,
    TicketForm,
    TicketUpdateForm,
    AssetForm,
    AssetAssignForm,
    TicketCommentForm,
)
from .models import Ticket, Asset, TicketComment
from .utils import is_it_admin


def login_view(request):
    """Login page with role-based redirect."""
    if request.user.is_authenticated:
        if is_it_admin(request.user):
            return redirect("admin_dashboard")
        return redirect("employee_dashboard")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if is_it_admin(user):
            return redirect("admin_dashboard")
        return redirect("employee_dashboard")

    return render(request, "support/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def employee_dashboard(request):
    """Employee dashboard with own tickets and assigned assets."""
    tickets = Ticket.objects.filter(employee=request.user)
    assets = Asset.objects.filter(assigned_to=request.user)
    
    # Statistics
    stats = {
        "total_tickets": tickets.count(),
        "open_tickets": tickets.filter(status="open").count(),
        "in_progress": tickets.filter(status="in_progress").count(),
        "resolved": tickets.filter(status="resolved").count(),
        "closed": tickets.filter(status="closed").count(),
        "high_urgency": tickets.filter(urgency="high", status__in=["open", "in_progress"]).count(),
        "total_assets": assets.count(),
    }
    
    # Recent tickets (last 5)
    recent_tickets = tickets[:5]
    
    # Pagination
    search_query = request.GET.get("search", "")
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "tickets": page_obj,
        "recent_tickets": recent_tickets,
        "assets": assets,
        "stats": stats,
        "search_query": search_query,
    }
    return render(request, "support/employee_dashboard.html", context)


@login_required
def raise_ticket(request):
    """Employee ticket creation."""
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.employee = request.user
            ticket.status = "open"
            ticket.save()
            messages.success(request, "Ticket created successfully!")
            return redirect("employee_dashboard")
    else:
        form = TicketForm()
    return render(request, "support/raise_ticket.html", {"form": form})


@login_required
def ticket_detail(request, pk):
    """Ticket detail view with comments."""
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Security: employees can only view their own tickets
    if not is_it_admin(request.user) and ticket.employee != request.user:
        messages.error(request, "You don't have permission to view this ticket.")
        return redirect("employee_dashboard")
    
    comments = ticket.comments.all()
    
    if request.method == "POST":
        comment_form = TicketCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.user = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect("ticket_detail", pk=pk)
    else:
        comment_form = TicketCommentForm()
    
    context = {
        "ticket": ticket,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "support/ticket_detail.html", context)


@login_required
@user_passes_test(is_it_admin)
def admin_dashboard(request):
    """IT admin dashboard with ticket filters and statistics."""
    status_filter = request.GET.get("status") or ""
    category_filter = request.GET.get("category") or ""
    urgency_filter = request.GET.get("urgency") or ""
    search_query = request.GET.get("search") or ""

    tickets = Ticket.objects.select_related("employee", "assigned_to").all()
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    if urgency_filter:
        tickets = tickets.filter(urgency=urgency_filter)
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(employee__username__icontains=search_query)
        )

    # Statistics
    all_tickets = Ticket.objects.all()
    stats = {
        "total": all_tickets.count(),
        "open": all_tickets.filter(status="open").count(),
        "in_progress": all_tickets.filter(status="in_progress").count(),
        "resolved": all_tickets.filter(status="resolved").count(),
        "closed": all_tickets.filter(status="closed").count(),
        "high_urgency": all_tickets.filter(urgency="high", status__in=["open", "in_progress"]).count(),
        "unassigned": all_tickets.filter(assigned_to__isnull=True, status__in=["open", "in_progress"]).count(),
    }
    
    # Category breakdown
    category_stats = (
        all_tickets.values("category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    
    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_tickets = all_tickets.filter(created_at__gte=week_ago).count()

    # Pagination
    paginator = Paginator(tickets, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "tickets": page_obj,
        "status_filter": status_filter,
        "category_filter": category_filter,
        "urgency_filter": urgency_filter,
        "search_query": search_query,
        "status_choices": Ticket.STATUS_CHOICES,
        "category_choices": Ticket.CATEGORY_CHOICES,
        "urgency_choices": Ticket.URGENCY_CHOICES,
        "stats": stats,
        "category_stats": category_stats,
        "recent_tickets": recent_tickets,
    }
    return render(request, "support/admin_dashboard.html", context)


@login_required
@user_passes_test(is_it_admin)
def admin_ticket_edit(request, pk):
    """Admin ticket management page."""
    ticket = get_object_or_404(Ticket, pk=pk)
    old_status = ticket.status
    old_assigned = ticket.assigned_to
    
    if request.method == "POST":
        # Handle comment submission separately
        if "add_comment" in request.POST:
            comment_form = TicketCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.user = request.user
                comment.save()
                messages.success(request, "Comment added successfully!")
                return redirect("admin_ticket_edit", pk=pk)
        else:
            form = TicketUpdateForm(request.POST, instance=ticket)
            if form.is_valid():
                ticket = form.save()
                # Add comment if status changed
                if old_status != ticket.status:
                    status_map = dict(Ticket.STATUS_CHOICES)
                    TicketComment.objects.create(
                        ticket=ticket,
                        user=request.user,
                        comment=f"Status changed from {status_map.get(old_status, old_status)} to {ticket.get_status_display()}",
                    )
                # Add comment if assignment changed
                if old_assigned != ticket.assigned_to:
                    old_name = old_assigned.get_full_name() if old_assigned else "Unassigned"
                    new_name = ticket.assigned_to.get_full_name() if ticket.assigned_to else "Unassigned"
                    TicketComment.objects.create(
                        ticket=ticket,
                        user=request.user,
                        comment=f"Ticket reassigned from {old_name} to {new_name}",
                    )
                messages.success(request, "Ticket updated successfully!")
                return redirect("admin_dashboard")
    else:
        form = TicketUpdateForm(instance=ticket)
        comment_form = TicketCommentForm()
    
    comments = ticket.comments.all()
    
    return render(
        request,
        "support/admin_ticket_edit.html",
        {
            "ticket": ticket,
            "form": form,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


@login_required
@user_passes_test(is_it_admin)
def asset_list(request):
    """List all assets for IT admin."""
    status_filter = request.GET.get("status") or ""
    search_query = request.GET.get("search") or ""
    
    assets = Asset.objects.select_related("assigned_to").all()
    
    if status_filter:
        assets = assets.filter(status=status_filter)
    if search_query:
        assets = assets.filter(
            Q(device_type__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(serial_number__icontains=search_query)
        )
    
    # Statistics
    stats = {
        "total": assets.count(),
        "in_use": Asset.objects.filter(status="in_use").count(),
        "available": Asset.objects.filter(status="available").count(),
        "under_repair": Asset.objects.filter(status="under_repair").count(),
        "warranty_expiring_soon": Asset.objects.filter(
            warranty_expiry__lte=datetime.now().date() + timedelta(days=30),
            warranty_expiry__gte=datetime.now().date()
        ).count(),
    }
    
    # Pagination
    paginator = Paginator(assets, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "support/asset_list.html", {
        "assets": page_obj,
        "stats": stats,
        "status_filter": status_filter,
        "search_query": search_query,
    })


@login_required
@user_passes_test(is_it_admin)
def asset_add(request):
    """Add new asset."""
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Asset added successfully!")
            return redirect("asset_list")
    else:
        form = AssetForm()
    return render(request, "support/asset_add.html", {"form": form})


@login_required
@user_passes_test(is_it_admin)
def asset_edit(request, pk):
    """Assign / update an asset."""
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        form = AssetAssignForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, "Asset updated successfully!")
            return redirect("asset_list")
    else:
        form = AssetAssignForm(instance=asset)
    return render(
        request,
        "support/asset_edit.html",
        {"asset": asset, "form": form},
    )


@login_required
def user_profile(request):
    """User profile page."""
    user = request.user
    tickets = Ticket.objects.filter(employee=user)
    assets = Asset.objects.filter(assigned_to=user)
    
    context = {
        "user": user,
        "total_tickets": tickets.count(),
        "total_assets": assets.count(),
    }
    return render(request, "support/user_profile.html", context)


@login_required
@user_passes_test(is_it_admin)
def export_tickets_csv(request):
    """Export tickets to CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="tickets_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        "ID", "Title", "Customer Name", "Customer Email", "Customer Phone", "Customer Alternate Phone",
        "Employee", "Category", "Urgency", "Status",
        "Assigned To", "Created At", "Description"
    ])
    
    tickets = Ticket.objects.select_related("employee", "assigned_to").all()
    for ticket in tickets:
        writer.writerow([
            ticket.id,
            ticket.title,
            ticket.customer_name or "",
            ticket.customer_email or "",
            ticket.customer_phone or "",
            ticket.customer_alternate_phone or "",
            ticket.employee.username,
            ticket.get_category_display(),
            ticket.get_urgency_display(),
            ticket.get_status_display(),
            ticket.assigned_to.username if ticket.assigned_to else "Unassigned",
            ticket.created_at.strftime("%Y-%m-%d %H:%M"),
            ticket.description[:100],  # Truncate long descriptions
        ])
    
    return response


def home(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if is_it_admin(request.user):
        return redirect("admin_dashboard")

    return redirect("employee_dashboard")