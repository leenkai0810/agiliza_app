from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuoteResponseViewSet, ServiceCategoryViewSet, ServiceRequestViewSet

app_name = "services"

router = DefaultRouter()
router.register("categories", ServiceCategoryViewSet, basename="category")
router.register("services/requests", ServiceRequestViewSet, basename="service-request")
router.register("services/quotes", QuoteResponseViewSet, basename="quote-response")

urlpatterns = [
    path("", include(router.urls)),
]
