from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.db.models import Q, Sum
from django.utils import timezone
from accounts.models import Review
from .models import QuoteResponse, ServiceCategory, ServiceRequest
from .serializers import (
    QuoteResponseSerializer,
    ServiceCategorySerializer,
    ServiceRequestSerializer,
    ServiceRequestStatusSerializer,
)


class ServiceCategoryViewSet(ReadOnlyModelViewSet):
    """Read-only API for active service categories."""

    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    print("ServiceCategoryViewSet initialized")
    print("Initial queryset count: ", ServiceCategory.objects.filter(is_active=True).count())
    def get_queryset(self):
        queryset = ServiceCategory.objects.filter(is_active=True)
        slug = self.request.query_params.get("slug")
        if slug:
            queryset = queryset.filter(slug=slug)
        return queryset


class ServiceRequestViewSet(ModelViewSet):
    """CRUD endpoints for service requests with status workflow support."""

    serializer_class = ServiceRequestSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     queryset = ServiceRequest.objects.select_related(
    #         "client",
    #         "professional_profile",
    #         "professional_profile__user",
    #         "category",
    #     )
    #     user = self.request.user

    #     if user.is_staff:
    #         return queryset

    #     professional_profile = getattr(user, "professional_profile", None)
    #     if professional_profile is not None:
    #         return queryset.filter(professional_profile=professional_profile) | queryset.filter(client=user)
        
    #     return queryset.filter(client=user)
    def get_queryset(self):
        queryset = ServiceRequest.objects.select_related(
            "client",
            "professional_profile",
            "professional_profile__user",
            "category",
        ).order_by("-created_at")

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        user = self.request.user
        if user.is_staff:
            return queryset

        professional_profile = getattr(user, "professional_profile", None)

        if professional_profile is not None:
            return queryset.filter(
                Q(professional_profile=professional_profile) |
                Q(professional_profile__isnull=True, status=ServiceRequest.Status.PENDING)
            )

        return queryset.filter(client=user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=["post"], url_path="status")
    def update_status(self, request, pk=None):
        service_request = self.get_object()
        serializer = ServiceRequestStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        next_status = serializer.validated_data["status"]
        try:
            service_request.transition_to(next_status)
        except ValueError as exc:
            raise ValidationError({"status": str(exc)}) from exc

        # If a professional accepts and the service_request has no professional assigned,
        # attach the acting user's professional profile (if any).
        if next_status == ServiceRequest.Status.ACCEPTED:
            acting_prof = getattr(request.user, "professional_profile", None)
            if acting_prof is not None and service_request.professional_profile is None:
                service_request.professional_profile = acting_prof
                service_request.save(
                    update_fields=("status", "professional_profile", "updated_at")
                )
            else:
                service_request.save(
                    update_fields=("status", "completed_at", "cancelled_at", "updated_at")
                )
        else:
            service_request.save(
                update_fields=("status", "completed_at", "cancelled_at", "updated_at")
            )

        return Response(
            ServiceRequestSerializer(service_request, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        professional_profile = getattr(request.user, "professional_profile", None)
        if professional_profile is None:
            return Response(
                {"detail": "Professional profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        now = timezone.now()
        pending_requests = ServiceRequest.objects.filter(
            Q(professional_profile=professional_profile)
            | Q(professional_profile__isnull=True, status=ServiceRequest.Status.PENDING),
        ).count()

        active_jobs = ServiceRequest.objects.filter(
            professional_profile=professional_profile,
            status__in=(ServiceRequest.Status.ACCEPTED, ServiceRequest.Status.SCHEDULED),
        ).count()

        completed_jobs = ServiceRequest.objects.filter(
            professional_profile=professional_profile,
            status=ServiceRequest.Status.COMPLETED,
        ).count()

        monthly_earnings = ServiceRequest.objects.filter(
            professional_profile=professional_profile,
            status=ServiceRequest.Status.COMPLETED,
            completed_at__year=now.year,
            completed_at__month=now.month,
            quoted_price__isnull=False,
        ).aggregate(total=Sum('quoted_price'))['total'] or 0

        upcoming_requests = ServiceRequest.objects.filter(
            professional_profile=professional_profile,
            status__in=(ServiceRequest.Status.ACCEPTED, ServiceRequest.Status.SCHEDULED),
        ).order_by('scheduled_date', 'requested_date')[:3]

        recent_reviews = Review.objects.filter(
            professional_profile=professional_profile,
        ).order_by('-created_at')[:3]

        return Response(
            {
                "full_name": request.user.full_name,
                "is_verified": request.user.is_verified,
                "online": request.user.is_active,
                "average_rating": float(professional_profile.average_rating),
                "pending_requests": pending_requests,
                "active_jobs": active_jobs,
                "completed_jobs": completed_jobs,
                "monthly_earnings": int(monthly_earnings),
                "upcoming_appointments": [
                    {
                        "id": str(request.id),
                        "title": request.title,
                        "scheduled_date": request.scheduled_date.isoformat() if request.scheduled_date else None,
                        "requested_date": request.requested_date.isoformat() if request.requested_date else None,
                        "status": request.status,
                        "address": request.address,
                    }
                    for request in upcoming_requests
                ],
                "recent_reviews": [
                    {
                        "id": str(review.id),
                        "rating": review.rating,
                        "comment": review.comment,
                        "created_at": review.created_at.isoformat() if review.created_at else None,
                    }
                    for review in recent_reviews
                ],
            },
            status=status.HTTP_200_OK,
        )


class QuoteResponseViewSet(ModelViewSet):
    """CRUD endpoints for professional quote responses."""

    serializer_class = QuoteResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = QuoteResponse.objects.select_related(
            "service_request",
            "service_request__client",
            "professional_profile",
            "professional_profile__user",
        )
        user = self.request.user

        if user.is_staff:
            return queryset

        professional_profile = getattr(user, "professional_profile", None)
        if professional_profile is not None:
            return queryset.filter(professional_profile=professional_profile) | queryset.filter(
                service_request__client=user
            )

        return queryset.filter(service_request__client=user)

    def perform_create(self, serializer):
        professional_profile = getattr(self.request.user, "professional_profile", None)
        if professional_profile is None:
            raise ValidationError(
                {"professional_profile": "Create a professional profile before sending quotes."}
            )

        service_request = serializer.validated_data["service_request"]
        if service_request.status not in (
            ServiceRequest.Status.PENDING,
            ServiceRequest.Status.QUOTED,
        ):
            raise ValidationError(
                {"service_request": "Quotes can only be sent for pending or quoted requests."}
            )

        quote_response = serializer.save(professional_profile=professional_profile)
        if service_request.status == ServiceRequest.Status.PENDING:
            service_request.transition_to(ServiceRequest.Status.QUOTED)
            service_request.quoted_price = quote_response.price
            service_request.professional_profile = professional_profile
            service_request.save(
                update_fields=(
                    "status",
                    "quoted_price",
                    "professional_profile",
                    "updated_at",
                )
            )
