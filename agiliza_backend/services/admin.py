from django.contrib import admin

from .models import QuoteResponse, ServiceCategory, ServiceRequest


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "professional_profile",
        "category",
        "status",
        "created_at",
    )
    list_filter = ("status", "category", "created_at")
    search_fields = (
        "title",
        "description",
        "client__email",
        "client__full_name",
        "professional_profile__user__email",
        "professional_profile__user__full_name",
    )
    autocomplete_fields = ("client", "professional_profile", "category")
    readonly_fields = ("created_at", "updated_at", "completed_at", "cancelled_at")


@admin.register(QuoteResponse)
class QuoteResponseAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "professional_profile",
        "price",
        "duration",
        "created_at",
    )
    search_fields = (
        "service_request__title",
        "professional_profile__user__email",
        "professional_profile__user__full_name",
        "message",
    )
    list_filter = ("created_at",)
    autocomplete_fields = ("service_request", "professional_profile")
    readonly_fields = ("created_at", "updated_at")
