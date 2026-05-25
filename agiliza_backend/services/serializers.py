from rest_framework import serializers

from .models import QuoteResponse, ServiceCategory, ServiceRequest
from accounts.serializers import ProfessionalProfileSerializer


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories."""

    class Meta:
        model = ServiceCategory
        fields = (
            "id",
            "name",
            "slug",
            "icon",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id",)

class ServiceRequestSerializer(serializers.ModelSerializer):
    """Serializer for service requests."""

    category = ServiceCategorySerializer(
        read_only=True,
    )

    professional_profile = ProfessionalProfileSerializer(
        read_only=True,
    )

    professional_profile_data = serializers.SerializerMethodField()

    category_id = serializers.UUIDField(
        write_only=True,
        required=False,
    )

    professional_profile_id = serializers.IntegerField(
        write_only=True,
        required=False,
    )

    class Meta:
        model = ServiceRequest

        fields = (
            "id",
            "client",

            "professional_profile",
            "professional_profile_data",

            "category",
            "category_id",

            "professional_profile_id",

            "title",
            "description",
            "status",

            "requested_date",
            "scheduled_date",

            "address",
            "latitude",
            "longitude",

            "quoted_price",

            "completed_at",
            "cancelled_at",

            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "client",
            "status",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        )

    def get_professional_profile_data(self, obj):
        if not obj.professional_profile:
            return None

        return {
            "id": obj.professional_profile.id,
            "full_name": obj.professional_profile.user.full_name,
            "bio": obj.professional_profile.bio,
            "hourly_rate": str(obj.professional_profile.hourly_rate),
            "rating": str(obj.professional_profile.average_rating),
        }

    def create(self, validated_data):
        category_id = validated_data.pop(
            "category_id",
            None,
        )

        professional_profile_id = validated_data.pop(
            "professional_profile_id",
            None,
        )

        if category_id:
            validated_data["category"] = ServiceCategory.objects.get(
                id=category_id,
            )

        if professional_profile_id:
            from accounts.models import ProfessionalProfile

            validated_data["professional_profile"] = ProfessionalProfile.objects.get(
                id=professional_profile_id,
            )

        return super().create(validated_data)

class ServiceRequestStatusSerializer(serializers.Serializer):
    """Serializer for service request status transitions."""

    status = serializers.ChoiceField(choices=ServiceRequest.Status.choices)


class QuoteResponseSerializer(serializers.ModelSerializer):
    """Serializer for professional quote responses."""

    professional_profile = ProfessionalProfileSerializer(read_only=True)
    service_request_data = ServiceRequestSerializer(
        source="service_request",
        read_only=True,
    )

    class Meta:
        model = QuoteResponse
        fields = (
            "id",
            "service_request",
            "service_request_data",
            "professional_profile",
            "price",
            "duration",
            "message",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "professional_profile",
            "created_at",
            "updated_at",
        )
