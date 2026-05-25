from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AvailabilitySlotViewSet,
    FavoriteViewSet,
    PortfolioItemViewSet,
    ProfessionalProfileViewSet,
    ReviewViewSet,
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    GoogleLoginView,
    GoogleConnectView,
    AppleLoginView,
    AppleConnectView,
    SocialAccountsListView,
    DisconnectSocialAccountView,
)

app_name = 'accounts'

router = DefaultRouter()
router.register('availability-slots', AvailabilitySlotViewSet, basename='availability-slot')
router.register('favorites', FavoriteViewSet, basename='favorite')
router.register('portfolio', PortfolioItemViewSet, basename='portfolio')
router.register('professionals', ProfessionalProfileViewSet, basename='professional')
router.register('reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # Traditional Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Social Authentication - Google
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('google/connect/', GoogleConnectView.as_view(), name='google-connect'),
    
    # Social Authentication - Apple
    path('apple/login/', AppleLoginView.as_view(), name='apple-login'),
    path('apple/connect/', AppleConnectView.as_view(), name='apple-connect'),
    
    # Social Accounts Management
    path('social/accounts/', SocialAccountsListView.as_view(), name='social-accounts-list'),
    path('social/disconnect/', DisconnectSocialAccountView.as_view(), name='social-disconnect'),
    path('', include(router.urls)),
]
