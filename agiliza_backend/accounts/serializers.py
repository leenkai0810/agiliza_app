from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    AvailabilitySlot,
    CustomUser,
    Favorite,
    PortfolioItem,
    ProfessionalProfile,
    Review,
)

from services.models import ServiceCategory


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'phone', 'role', 'password', 'password_confirm')
        extra_kwargs = {
            'full_name': {'required': True},
        }

    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )
        return data

    def validate_email(self, value):
        """Check if email already exists."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        role = validated_data.get('role', 'CLIENT')
        user = CustomUser.objects.create_user(**validated_data)
        if role == 'PROFESSIONAL':
            ProfessionalProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': '',
                    'years_experience': 0,
                    'hourly_rate': 0,
                    'service_radius_km': 10,
                    'address': '',
                },
            )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate user with email and password."""
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError('Email and password are required.')

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'Invalid credentials. Please check your email and password.'
            )

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'full_name',
            'phone',
            'profile_image',
            'role',
            'is_verified',
            'is_active',
            'date_joined',
        )
        read_only_fields = ('id', 'email', 'is_verified', 'date_joined')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = CustomUser
        fields = ('full_name', 'phone', 'profile_image')

class ProfessionalUserSerializer(serializers.ModelSerializer):
    """Nested serializer for professional user details."""

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'full_name',
            'email',
            'phone',
            'profile_image',
        )


class ServiceCategoryNestedSerializer(serializers.Serializer):
    """Nested serializer for service categories."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    icon = serializers.ImageField(read_only=True)


class PortfolioItemSerializer(serializers.ModelSerializer):
    """Serializer for professional portfolio items."""

    class Meta:
        model = PortfolioItem
        fields = (
            'id',
            'professional_profile',
            'title',
            'description',
            'image',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'professional_profile', 'created_at', 'updated_at')

class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """Serializer for weekly professional availability slots."""

    class Meta:
        model = AvailabilitySlot
        fields = (
            'id',
            'professional_profile',
            'day_of_week',
            'start_time',
            'end_time',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'professional_profile', 'created_at', 'updated_at')

    def validate(self, data):
        start_time = data.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = data.get('end_time', getattr(self.instance, 'end_time', None))
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {'end_time': 'End time must be after start time.'}
            )
        return data

class ProfessionalProfileSerializer(serializers.ModelSerializer):
    """Serializer for professional profile details."""

    user = ProfessionalUserSerializer(read_only=True)

    service_categories = ServiceCategoryNestedSerializer(
        many=True,
        read_only=True,
    )
    portfolio = PortfolioItemSerializer(
        source='portfolio_items',
        many=True,
        read_only=True,
    )
    availability = AvailabilitySlotSerializer(
        source='availability_slots',
        many=True,
        read_only=True,
    )

    class Meta:
        model = ProfessionalProfile
        fields = (
            'id',
            'user',
            'bio',
            'years_experience',
            'hourly_rate',
            'service_categories',
            'portfolio',
            'availability',
            'service_radius_km',
            'address',
            'latitude',
            'longitude',
            'average_rating',
            'total_reviews',
        )

        read_only_fields = (
            'id',
            'average_rating',
            'total_reviews',
        )


class ProfessionalProfileUpdateSerializer(serializers.ModelSerializer):
    """Writable fields for the authenticated professional's own profile."""

    category_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = ProfessionalProfile
        fields = (
            'bio',
            'years_experience',
            'hourly_rate',
            'service_radius_km',
            'address',
            'latitude',
            'longitude',
            'category_ids',
        )

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        instance = super().update(instance, validated_data)
        if category_ids is not None:
            categories = ServiceCategory.objects.filter(id__in=category_ids, is_active=True)
            instance.service_categories.set(categories)
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for saved professionals."""

    professional = ProfessionalProfileSerializer(
        source='professional_profile',
        read_only=True,
    )

    class Meta:
        model = Favorite

        fields = (
            'id',
            'client',
            'professional_profile',
            'professional',
            'created_at',
        )

        read_only_fields = (
            'id',
            'client',
            'created_at',
        )

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for professional reviews."""

    service_request_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Review
        fields = (
            'id',
            'client',
            'professional_profile',
            'service_request_id',
            'rating',
            'comment',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'client', 'created_at', 'updated_at')

    def validate(self, data):
        from services.models import ServiceRequest

        professional_profile = data.get('professional_profile')
        service_request_id = data.get('service_request_id')
        request = self.context.get('request')

        if professional_profile and request and request.user.is_authenticated:
            completed_qs = ServiceRequest.objects.filter(
                client=request.user,
                professional_profile=professional_profile,
                status=ServiceRequest.Status.COMPLETED,
            )
            if service_request_id:
                completed_qs = completed_qs.filter(id=service_request_id)
            if not completed_qs.exists():
                raise serializers.ValidationError(
                    {
                        'professional_profile': (
                            'You can only review a professional after a completed service request.'
                        )
                    }
                )
        return data


class TokenSerializer(serializers.Serializer):
    """Serializer for JWT tokens."""

    access = serializers.CharField()
    refresh = serializers.CharField()


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google OAuth authentication."""

    id_token = serializers.CharField(required=False)
    access_token = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

    def validate(self, data):
        """Validate that at least one token is provided."""
        if not any([data.get('id_token'), data.get('access_token'), data.get('code')]):
            raise serializers.ValidationError(
                'Either id_token, access_token, or code is required.'
            )
        return data


class AppleAuthSerializer(serializers.Serializer):
    """Serializer for Apple OAuth authentication."""

    id_token = serializers.CharField(required=False)
    access_token = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
    user = serializers.JSONField(required=False)  # User details from Apple

    def validate(self, data):
        """Validate that at least one token is provided."""
        if not any([data.get('id_token'), data.get('access_token'), data.get('code')]):
            raise serializers.ValidationError(
                'Either id_token, access_token, or code is required.'
            )
        return data


class SocialAuthResponseSerializer(serializers.Serializer):
    """Serializer for social auth response."""

    user = UserProfileSerializer()
    tokens = TokenSerializer()
    is_new_user = serializers.BooleanField()


class ConnectSocialAccountSerializer(serializers.Serializer):
    """Serializer for connecting a social account to existing user."""

    provider = serializers.ChoiceField(choices=['google', 'apple'])
    id_token = serializers.CharField(required=False)
    access_token = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
