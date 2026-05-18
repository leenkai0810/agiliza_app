from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for handling account creation and updates."""

    def save_user(self, request, sociallogin, form=None):
        """Save user instance with custom fields."""
        user = super().save_user(request, sociallogin, form)
        
        # Extract additional info from social account
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            # Get full name from Google
            if 'name' in extra_data:
                user.full_name = extra_data.get('name', '')
            # Mark as verified if email is verified by provider
            if extra_data.get('verified_email'):
                user.is_verified = True
        
        elif sociallogin.account.provider == 'apple':
            # Apple might not provide full name in extra_data every time
            extra_data = sociallogin.account.extra_data
            if 'name' in extra_data:
                user.full_name = extra_data.get('name', '')
        
        # Set role default
        if not user.role:
            user.role = 'CLIENT'
        
        user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for handling social authentication."""

    def pre_social_login(self, request, sociallogin):
        """Called after successful provider authentication."""
        # Check if user already exists
        if sociallogin.is_existing:
            return

        # Allow connecting the social account to an existing account
        # (if the email matches)
        try:
            from .models import CustomUser
            user = CustomUser.objects.get(email=sociallogin.account.extra_data.get('email'))
            sociallogin.connect(request, user)
        except CustomUser.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        """Populate user instance with data from social provider."""
        user = super().populate_user(request, sociallogin, data)
        
        # Ensure we have a full_name
        if 'name' in data:
            user.full_name = data.get('name', '')
        
        return user

    def save_user(self, request, sociallogin, form=None):
        """Save the user with custom field handling."""
        user = super().save_user(request, sociallogin, form)
        
        # Ensure role is set
        if not user.role:
            user.role = 'CLIENT'
        
        user.save()
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """Get redirect URL after connecting social account."""
        return '/accounts/social/connected/'

    def get_login_redirect_url(self, request):
        """Get redirect URL after social login."""
        return '/accounts/social/login-success/'
