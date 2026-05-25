from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import logout
from math import asin, cos, radians, sin, sqrt
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView, SocialConnectView

from .models import (
    AvailabilitySlot,
    CustomUser,
    Favorite,
    PortfolioItem,
    ProfessionalProfile,
    Review,
)
from .serializers import (
    AvailabilitySlotSerializer,
    FavoriteSerializer,
    PortfolioItemSerializer,
    ProfessionalProfileSerializer,
    ReviewSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    TokenSerializer,
    GoogleAuthSerializer,
    AppleAuthSerializer,
    SocialAuthResponseSerializer,
)


def _distance_km(latitude_a, longitude_a, latitude_b, longitude_b):
    earth_radius_km = 6371
    lat_delta = radians(latitude_b - latitude_a)
    lon_delta = radians(longitude_b - longitude_a)
    a = (
        sin(lat_delta / 2) ** 2
        + cos(radians(latitude_a))
        * cos(radians(latitude_b))
        * sin(lon_delta / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))


class ProfessionalProfileViewSet(ReadOnlyModelViewSet):
    """Read-only professional search API with category, rating, and location filters."""

    serializer_class = ProfessionalProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ProfessionalProfile.objects.select_related('user').prefetch_related(
            'service_categories'
        )
        print("Initial queryset count: ", queryset.count())
        params = self.request.query_params
        print("Query params are: ", params)
        category = params.get('category')
        print("Category filter is: ", category)
        if category:
            queryset = queryset.filter(service_categories__slug=category)
            if category.isdigit():
                queryset = queryset | ProfessionalProfile.objects.filter(
                    service_categories__id=category
                )

        min_rating = params.get('min_rating') or params.get('rating')
        print("Rating filter is: ", min_rating)
        if min_rating:
            try:
                min_rating = float(min_rating)
            except ValueError as exc:
                raise ValidationError(
                    {'min_rating': 'min_rating must be a number.'}
                ) from exc
            queryset = queryset.filter(average_rating__gte=min_rating)

        latitude = params.get('latitude') or params.get('lat')
        longitude = params.get('longitude') or params.get('lng') or params.get('lon')
        radius_km = params.get('radius_km')
        if latitude and longitude and radius_km:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                radius_km = float(radius_km)
            except ValueError as exc:
                raise ValidationError(
                    {'location': 'latitude, longitude, and radius_km must be numbers.'}
                ) from exc

            queryset = queryset.filter(latitude__isnull=False, longitude__isnull=False)
            matching_ids = [
                professional.id
                for professional in queryset
                if _distance_km(
                    latitude,
                    longitude,
                    float(professional.latitude),
                    float(professional.longitude),
                )
                <= radius_km
            ]
            queryset = ProfessionalProfile.objects.filter(id__in=matching_ids)

        return queryset.distinct().order_by('-average_rating', '-total_reviews')

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        if request.user.role != 'PROFESSIONAL':
            return Response(
                {'detail': 'Only professional users may access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        professional_profile = getattr(request.user, 'professional_profile', None)
        if professional_profile is None:
            return Response(
                {'detail': 'Professional profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            professional_profile
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class PortfolioItemViewSet(ModelViewSet):
    """CRUD endpoints for the authenticated professional's portfolio items."""

    serializer_class = PortfolioItemSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return PortfolioItem.objects.filter(
            professional_profile__user=self.request.user
        ).select_related('professional_profile', 'professional_profile__user')

    def perform_create(self, serializer):
        professional_profile = getattr(self.request.user, 'professional_profile', None)
        if professional_profile is None:
            raise ValidationError(
                {'professional_profile': 'Create a professional profile before adding portfolio items.'}
            )
        serializer.save(professional_profile=professional_profile)


class AvailabilitySlotViewSet(ModelViewSet):
    """CRUD endpoints for the authenticated professional's weekly availability."""

    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AvailabilitySlot.objects.filter(
            professional_profile__user=self.request.user
        ).select_related('professional_profile', 'professional_profile__user')

    def perform_create(self, serializer):
        professional_profile = getattr(self.request.user, 'professional_profile', None)
        if professional_profile is None:
            raise ValidationError(
                {'professional_profile': 'Create a professional profile before adding availability slots.'}
            )
        serializer.save(professional_profile=professional_profile)


class FavoriteViewSet(ModelViewSet):
    """CRUD endpoints for the authenticated client's saved professionals."""

    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(client=self.request.user).select_related(
            'client',
            'professional_profile',
            'professional_profile__user',
        )

    def perform_create(self, serializer):
        professional_profile = serializer.validated_data['professional_profile']
        if professional_profile.user_id == self.request.user.id:
            raise ValidationError(
                {'professional_profile': 'You cannot save your own professional profile.'}
            )
        serializer.save(client=self.request.user)


class ReviewViewSet(ModelViewSet):
    """CRUD endpoints for authenticated clients' professional reviews."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Review.objects.select_related(
            'client',
            'professional_profile',
            'professional_profile__user',
        )
        user = self.request.user

        if user.is_staff:
            return queryset

        professional_profile = getattr(user, 'professional_profile', None)
        if professional_profile is not None:
            return queryset.filter(professional_profile=professional_profile) | queryset.filter(client=user)

        return queryset.filter(client=user)

    def perform_create(self, serializer):
        professional_profile = serializer.validated_data['professional_profile']
        if professional_profile.user_id == self.request.user.id:
            raise ValidationError(
                {'professional_profile': 'You cannot review your own professional profile.'}
            )
        serializer.save(client=self.request.user)


class UserRegistrationView(APIView):
    """API view for user registration."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        print("Serializer is: ",serializer)
        if serializer.is_valid():
            print("Serializer is valid")
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
