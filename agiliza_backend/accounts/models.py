from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Custom user manager for handling user creation with email as the username field."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the unique identifier."""

    ROLE_CHOICES = [
        ('CLIENT', 'Client'),
        ('PROFESSIONAL', 'Professional'),
        ('ADMIN', 'Admin'),
    ]

    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CLIENT'
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name.strip()

    def get_short_name(self):
        return self.email


class ProfessionalProfile(models.Model):
    """Extended profile details for professional users."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='professional_profile',
    )
    bio = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_categories = models.ManyToManyField(
        'services.ServiceCategory',
        related_name='professional_profiles',
        blank=True,
    )
    service_radius_km = models.PositiveIntegerField(default=0)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Professional profile'
        verbose_name_plural = 'Professional profiles'

    def __str__(self):
        return f'{self.user.email} professional profile'


class PortfolioItem(models.Model):
    """Portfolio work sample uploaded by a professional."""

    professional_profile = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name='portfolio_items',
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='portfolio_items/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class AvailabilitySlot(models.Model):
    """Reusable weekly availability slot for a professional."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    professional_profile = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name='availability_slots',
    )
    day_of_week = models.PositiveSmallIntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('professional_profile', 'day_of_week', 'start_time', 'end_time'),
                name='unique_availability_slot_per_professional',
            ),
        ]
        ordering = ('day_of_week', 'start_time')

    def __str__(self):
        day = self.get_day_of_week_display()
        return f'{self.professional_profile.user.email}: {day} {self.start_time}-{self.end_time}'

    def clean(self):
        super().clean()
        if self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'End time must be after start time.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Favorite(models.Model):
    """Professional saved by a client."""

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_professionals',
    )
    professional_profile = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('client', 'professional_profile'),
                name='unique_favorite_professional_per_client',
            ),
        ]
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.client.email} saved {self.professional_profile.user.email}'


class Review(models.Model):
    """Client review for a professional profile."""

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    professional_profile = models.ForeignKey(
        ProfessionalProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('client', 'professional_profile'),
                name='unique_review_per_client_professional',
            ),
        ]
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.rating}/5 review for {self.professional_profile.user.email}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_professional_rating()

    def delete(self, *args, **kwargs):
        professional_profile = self.professional_profile
        result = super().delete(*args, **kwargs)
        self.update_professional_rating(professional_profile)
        return result

    def update_professional_rating(self, professional_profile=None):
        professional_profile = professional_profile or self.professional_profile
        summary = professional_profile.reviews.aggregate(
            average_rating=models.Avg('rating'),
            total_reviews=models.Count('id'),
        )
        professional_profile.average_rating = round(summary['average_rating'] or 0, 2)
        professional_profile.total_reviews = summary['total_reviews']
        professional_profile.save(update_fields=('average_rating', 'total_reviews'))
