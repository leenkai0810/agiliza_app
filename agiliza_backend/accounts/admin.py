from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    AvailabilitySlot,
    CustomUser,
    Favorite,
    PortfolioItem,
    ProfessionalProfile,
    Review,
)


class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for CustomUser model."""

    list_display = ('email', 'full_name', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'full_name', 'phone')
    ordering = ('-date_joined',)
    list_editable = ('role', 'is_verified')
    list_display_links = ('email', 'full_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'profile_image')}),
        ('User Status', {
            'fields': ('role', 'is_verified', 'is_active', 'is_staff'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name', 'phone', 'role')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'years_experience',
        'hourly_rate',
        'service_radius_km',
        'average_rating',
        'total_reviews',
    )
    search_fields = ('user__email', 'user__full_name', 'address')
    list_filter = ('years_experience', 'average_rating')
    autocomplete_fields = ('user',)
    filter_horizontal = ('service_categories',)


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'professional_profile', 'created_at')
    search_fields = (
        'title',
        'description',
        'professional_profile__user__email',
        'professional_profile__user__full_name',
    )
    list_filter = ('created_at',)
    autocomplete_fields = ('professional_profile',)


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = (
        'professional_profile',
        'day_of_week',
        'start_time',
        'end_time',
        'is_active',
    )
    list_filter = ('day_of_week', 'is_active')
    search_fields = (
        'professional_profile__user__email',
        'professional_profile__user__full_name',
    )
    autocomplete_fields = ('professional_profile',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('client', 'professional_profile', 'created_at')
    search_fields = (
        'client__email',
        'client__full_name',
        'professional_profile__user__email',
        'professional_profile__user__full_name',
    )
    list_filter = ('created_at',)
    autocomplete_fields = ('client', 'professional_profile')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'client',
        'professional_profile',
        'rating',
        'created_at',
    )
    search_fields = (
        'client__email',
        'client__full_name',
        'professional_profile__user__email',
        'professional_profile__user__full_name',
        'comment',
    )
    list_filter = ('rating', 'created_at')
    autocomplete_fields = ('client', 'professional_profile')
    readonly_fields = ('created_at', 'updated_at')
