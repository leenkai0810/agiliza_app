from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser


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
        user = CustomUser.objects.create_user(**validated_data)
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
