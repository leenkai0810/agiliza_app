from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, ProfessionalProfile


class AuthAndProfessionalProfileTests(APITestCase):
    def test_professional_registration_creates_profile(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'email': 'pro@milestone2.test',
                'password': 'TestPass123!',
                'password_confirm': 'TestPass123!',
                'full_name': 'Pro User',
                'phone': '9999999999',
                'role': 'PROFESSIONAL',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = CustomUser.objects.get(email='pro@milestone2.test')
        self.assertTrue(ProfessionalProfile.objects.filter(user=user).exists())

    def test_professional_can_patch_me_profile(self):
        user = CustomUser.objects.create_user(
            email='patchme@milestone2.test',
            password='TestPass123!',
            full_name='Patch Me',
            role='PROFESSIONAL',
        )
        ProfessionalProfile.objects.create(user=user, bio='Initial bio')

        self.client.force_authenticate(user=user)
        response = self.client.patch(
            reverse('accounts:professional-me'),
            {
                'bio': 'Updated bio with enough detail for clients.',
                'hourly_rate': '75.00',
                'service_radius_km': 20,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.professional_profile.refresh_from_db()
        self.assertIn('Updated bio', user.professional_profile.bio)
