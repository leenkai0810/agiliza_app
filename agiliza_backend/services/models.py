import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from accounts.models import ProfessionalProfile


class ServiceCategory(models.Model):
    """Category used to group services offered on the platform."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.ImageField(upload_to="categories/", null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service category"
        verbose_name_plural = "Service categories"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class ServiceRequest(models.Model):
    """Request from a client for a professional service."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        QUOTED = "QUOTED", "Quoted"
        ACCEPTED = "ACCEPTED", "Accepted"
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    STATUS_TRANSITIONS = {
        # Allow direct acceptance from PENDING so professionals can accept client-assigned
        # requests without creating a quoted state first.
        Status.PENDING: {Status.QUOTED, Status.CANCELLED, Status.ACCEPTED},
        Status.QUOTED: {Status.ACCEPTED, Status.CANCELLED},
        Status.ACCEPTED: {Status.SCHEDULED, Status.CANCELLED},
        Status.SCHEDULED: {Status.COMPLETED, Status.CANCELLED},
        Status.COMPLETED: set(),
        Status.CANCELLED: set(),
    }

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_requests",
    )
    professional_profile = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.SET_NULL,
        related_name="service_requests",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        related_name="service_requests",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    requested_date = models.DateTimeField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def can_transition_to(self, status):
        return status in self.STATUS_TRANSITIONS[self.status]

    def transition_to(self, status):
        if not self.can_transition_to(status):
            raise ValueError(f"Cannot transition from {self.status} to {status}.")

        self.status = status
        if status == self.Status.COMPLETED:
            self.completed_at = timezone.now()
        elif status == self.Status.CANCELLED:
            self.cancelled_at = timezone.now()


class QuoteResponse(models.Model):
    """Quote sent by a professional for a service request."""

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="quote_responses",
    )
    professional_profile = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name="quote_responses",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("service_request", "professional_profile"),
                name="unique_quote_response_per_professional",
            ),
        ]
        ordering = ("-created_at",)

    def __str__(self):
        return f"Quote for {self.service_request} by {self.professional_profile.user.email}"
