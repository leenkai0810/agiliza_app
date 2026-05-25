from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, ProfessionalProfile
from services.models import ServiceCategory, ServiceRequest, QuoteResponse


class ServiceRequestAndQuoteTests(APITestCase):
    def setUp(self):
        self.client_user = CustomUser.objects.create_user(
            email='client@milestone2.test',
            password='TestPass123!',
            full_name='Client User',
            role='CLIENT',
        )
        self.pro_user = CustomUser.objects.create_user(
            email='provider@milestone2.test',
            password='TestPass123!',
            full_name='Provider User',
            role='PROFESSIONAL',
        )
        self.pro_profile = ProfessionalProfile.objects.create(
            user=self.pro_user,
            bio='Experienced provider',
        )
        self.category = ServiceCategory.objects.create(
            name='Plumbing',
            slug='plumbing',
            is_active=True,
        )

    def test_client_can_create_service_request(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(
            reverse('services:service-request-list'),
            {
                'title': 'Fix kitchen sink',
                'description': 'Need urgent plumbing help for leaking sink.',
                'address': '221B Baker Street, London',
                'category_id': str(self.category.id),
                'professional_profile_id': self.pro_profile.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request_id = response.data['id']
        service_request = ServiceRequest.objects.get(id=request_id)
        self.assertEqual(service_request.client_id, self.client_user.id)
        self.assertEqual(service_request.professional_profile_id, self.pro_profile.id)

    def test_professional_can_send_quote(self):
        service_request = ServiceRequest.objects.create(
            client=self.client_user,
            category=self.category,
            title='Paint living room',
            description='Need interior painting for one room.',
            status=ServiceRequest.Status.PENDING,
        )

        self.client.force_authenticate(user=self.pro_user)
        response = self.client.post(
            reverse('services:quote-response-list'),
            {
                'service_request': str(service_request.id),
                'price': '120.00',
                'duration': '2 days',
                'message': 'I can start tomorrow.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(QuoteResponse.objects.filter(service_request=service_request).count(), 1)
        service_request.refresh_from_db()
        self.assertEqual(service_request.status, ServiceRequest.Status.QUOTED)

    def test_client_can_accept_quoted_request(self):
        service_request = ServiceRequest.objects.create(
            client=self.client_user,
            professional_profile=self.pro_profile,
            category=self.category,
            title='AC repair',
            description='Air conditioner not cooling properly.',
            status=ServiceRequest.Status.QUOTED,
            quoted_price='90.00',
        )

        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(
            reverse('services:service-request-update-status', kwargs={'pk': service_request.id}),
            {'status': ServiceRequest.Status.ACCEPTED},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_request.refresh_from_db()
        self.assertEqual(service_request.status, ServiceRequest.Status.ACCEPTED)
