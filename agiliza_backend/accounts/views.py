from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import logout
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView, SocialConnectView

from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    TokenSerializer,
    GoogleAuthSerializer,
    AppleAuthSerializer,
    SocialAuthResponseSerializer,
)


class UserRegistrationView(APIView):
    """API view for user registration."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'message': 'User registered successfully.',
                    'user': UserProfileSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """API view for user login."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate user and return tokens."""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'message': 'Login successful.',
                    'user': UserProfileSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """API view for user logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Logout user and invalidate tokens."""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            logout(request)
            return Response(
                {'message': 'Logout successful.'},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(APIView):
    """API view for retrieving and updating user profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve current user profile."""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """Update user profile."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Profile updated successfully.',
                    'user': UserProfileSerializer(request.user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Partially update user profile."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Profile updated successfully.',
                    'user': UserProfileSerializer(request.user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(SocialLoginView):
    """Google OAuth2 login view."""

    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:8000/api/auth/google/callback/'

    def post(self, request, *args, **kwargs):
        """Handle Google OAuth2 login."""
        serializer = GoogleAuthSerializer(data=request.data)
        if serializer.is_valid():
            return super().post(request, *args, **kwargs)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleConnectView(SocialConnectView):
    """Connect Google account to existing user."""

    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:8000/api/auth/google/callback/'
    permission_classes = [IsAuthenticated]


class AppleLoginView(SocialLoginView):
    """Apple OAuth2 login view."""

    adapter_class = AppleOAuth2Adapter
    callback_url = 'http://localhost:8000/api/auth/apple/callback/'

    def post(self, request, *args, **kwargs):
        """Handle Apple OAuth2 login."""
        serializer = AppleAuthSerializer(data=request.data)
        if serializer.is_valid():
            return super().post(request, *args, **kwargs)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppleConnectView(SocialConnectView):
    """Connect Apple account to existing user."""

    adapter_class = AppleOAuth2Adapter
    callback_url = 'http://localhost:8000/api/auth/apple/callback/'
    permission_classes = [IsAuthenticated]


class SocialAccountsListView(APIView):
    """List all connected social accounts for current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all connected social accounts."""
        social_accounts = SocialAccount.objects.filter(user=request.user)
        
        accounts_list = [
            {
                'provider': account.provider,
                'display_name': account.get_provider().name,
                'connected_at': account.date_joined,
                'is_primary': account.user.email == account.extra_data.get('email'),
            }
            for account in social_accounts
        ]
        
        return Response({
            'social_accounts': accounts_list,
            'total': len(accounts_list),
        }, status=status.HTTP_200_OK)


class DisconnectSocialAccountView(APIView):
    """Disconnect a social account from user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Disconnect a social account."""
        provider = request.data.get('provider')
        
        if not provider:
            return Response(
                {'error': 'Provider is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            social_account = SocialAccount.objects.get(
                user=request.user,
                provider=provider
            )
            social_account.delete()
            return Response(
                {'message': f'{provider.capitalize()} account disconnected successfully.'},
                status=status.HTTP_200_OK,
            )
        except SocialAccount.DoesNotExist:
            return Response(
                {'error': f'No {provider} account connected.'},
                status=status.HTTP_404_NOT_FOUND,
            )

