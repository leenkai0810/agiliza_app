# FILE: seed/seed_milestone2.py

import os
import sys
import random

from decimal import Decimal
from datetime import time, timedelta
from pathlib import Path

# =====================================================
# DJANGO SETUP
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model

from services.models import (
    ServiceCategory,
    ServiceRequest,
    QuoteResponse,
)

from accounts.models import (
    ProfessionalProfile,
    PortfolioItem,
    AvailabilitySlot,
    Favorite,
    Review,
)

User = get_user_model()

print("\n🚀 Starting Milestone 2 Seed Script...\n")

# =====================================================
# HELPERS
# =====================================================

def create_user_if_not_exists(email, role, full_name):

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "full_name": full_name,
            "role": role,
            "phone": str(random.randint(9000000000, 9999999999)),
            "is_active": True,
            "is_verified": True,
        }
    )

    if created:
        user.set_password("Test@123")
        user.save()
        print(f"✅ Created user: {email}")
    else:
        print(f"⏩ User already exists: {email}")

    return user


# =====================================================
# SERVICE CATEGORIES
# =====================================================

categories_data = [
    ("Plumbing", "plumbing"),
    ("Electrical", "electrical"),
    ("Cleaning", "cleaning"),
    ("Painting", "painting"),
    ("Carpentry", "carpentry"),
    ("HVAC", "hvac"),
    ("Appliance Repair", "appliance-repair"),
    ("Gardening", "gardening"),
]

categories = []

for name, slug in categories_data:

    category, created = ServiceCategory.objects.get_or_create(
        slug=slug,
        defaults={
            "name": name,
            "description": f"{name} services",
            "is_active": True,
        }
    )

    if created:
        print(f"✅ Category created: {name}")
    else:
        print(f"⏩ Category exists: {name}")

    categories.append(category)


# =====================================================
# CLIENT USERS
# =====================================================

clients = []

for i in range(1, 6):

    client = create_user_if_not_exists(
        email=f"client{i}@test.com",
        role="CLIENT",
        full_name=f"Client {i}"
    )

    clients.append(client)


# =====================================================
# PROFESSIONAL USERS
# =====================================================

professional_types = [
    "plumber",
    "electrician",
    "cleaner",
    "painter",
    "carpenter",
    "hvac",
    "gardener",
    "repairman",
    "technician",
    "mechanic",
]

professionals = []

for prof in professional_types:

    user = create_user_if_not_exists(
        email=f"{prof}@test.com",
        role="PROFESSIONAL",
        full_name=prof.title()
    )

    professionals.append(user)

    profile, created = ProfessionalProfile.objects.get_or_create(
        user=user,
        defaults={
            "bio": f"Professional {prof} with years of experience",
            "years_experience": random.randint(3, 15),
            "hourly_rate": Decimal(random.randint(15, 50)),
            "service_radius_km": 15,
            "address": "New Delhi, India",
            "latitude": Decimal("28.6139"),
            "longitude": Decimal("77.2090"),
            "average_rating": Decimal(str(round(random.uniform(4.0, 5.0), 1))),
            "total_reviews": random.randint(10, 100),
        }
    )

    if created:
        print(f"✅ Professional profile created: {user.email}")
    else:
        print(f"⏩ Professional profile exists: {user.email}")

    # ADD CATEGORIES TO PROFESSIONAL
    random_categories = random.sample(
        categories,
        random.randint(1, 3)
    )

    profile.service_categories.set(random_categories)


# =====================================================
# AVAILABILITY SLOTS
# =====================================================

days = [
    (1, "MONDAY"),
    (2, "TUESDAY"),
    (3, "WEDNESDAY"),
    (4, "THURSDAY"),
    (5, "FRIDAY"),
]
for user in professionals:

    profile = ProfessionalProfile.objects.get(user=user)

    for day_value, day_name in days:

        exists = AvailabilitySlot.objects.filter(
            professional_profile=profile,
            day_of_week=day_value,
        ).exists()

        if exists:
            print(f"⏩ Availability exists: {user.email} {day_name}")
            continue

        AvailabilitySlot.objects.create(
            professional_profile=profile,
            day_of_week=day_value,
            start_time=time(9, 0),
            end_time=time(18, 0),
            is_active=True,
        )

        print(f"✅ Availability created: {user.email} {day_name}")
        
# =====================================================
# PORTFOLIO ITEMS
# =====================================================

portfolio_titles = [
    "Kitchen Repair",
    "Bathroom Installation",
    "Office Wiring",
    "Wall Painting",
    "Garden Setup",
]

for user in professionals:

    profile = ProfessionalProfile.objects.get(user=user)

    for title in portfolio_titles:

        exists = PortfolioItem.objects.filter(
            professional_profile=profile,
            title=title,
        ).exists()

        if exists:
            print(f"⏩ Portfolio exists: {user.email} - {title}")
            continue

        PortfolioItem.objects.create(
            professional_profile=profile,
            title=title,
            description=f"{title} completed professionally.",
        )

        print(f"✅ Portfolio created: {user.email} - {title}")


# =====================================================
# FAVORITES
# =====================================================

for client in clients:

    random_pros = random.sample(professionals, 3)

    for pro_user in random_pros:

        profile = ProfessionalProfile.objects.get(user=pro_user)

        fav, created = Favorite.objects.get_or_create(
            client=client,
            professional_profile=profile,
        )

        if created:
            print(f"✅ Favorite added: {client.email} -> {pro_user.email}")
        else:
            print(f"⏩ Favorite exists")


# =====================================================
# SERVICE REQUESTS
# =====================================================

statuses = [
    "PENDING",
    "QUOTED",
    "ACCEPTED",
    "SCHEDULED",
    "COMPLETED",
]

requests_created = []

for i in range(20):

    client = random.choice(clients)

    professional_user = random.choice(professionals)

    professional_profile = ProfessionalProfile.objects.get(
        user=professional_user
    )

    category = random.choice(categories)

    title = f"{category.name} Service Request {i+1}"

    request, created = ServiceRequest.objects.get_or_create(
        title=title,
        client=client,
        professional_profile=professional_profile,
        defaults={
            "category": category,
            "description": f"Need help with {category.name.lower()}",
            "requested_date": timezone.now() + timedelta(days=random.randint(1, 7)),
            "address": "New Delhi",
            "status": random.choice(statuses),
            "quoted_price": Decimal(random.randint(500, 5000)),
        }
    )

    if created:
        print(f"✅ Request created: {title}")
    else:
        print(f"⏩ Request exists: {title}")

    requests_created.append(request)


# =====================================================
# QUOTE RESPONSES
# =====================================================

for request in requests_created[:10]:

    exists = QuoteResponse.objects.filter(
        service_request=request
    ).exists()

    if exists:
        print(f"⏩ Quote exists")
        continue

    QuoteResponse.objects.create(
        service_request=request,
        professional_profile=request.professional_profile,
        price=Decimal(random.randint(500, 5000)),
        duration="2 hours",
        message="Can complete same day.",
    )

    print(f"✅ Quote created")


# =====================================================
# REVIEWS
# =====================================================

review_comments = [
    "Excellent service",
    "Very professional",
    "Quick response",
    "Highly recommended",
    "Clean and efficient work",
]

for professional_user in professionals:

    profile = ProfessionalProfile.objects.get(
        user=professional_user
    )

    for client in random.sample(clients, 3):

        exists = Review.objects.filter(
            client=client,
            professional_profile=profile,
        ).exists()

        if exists:
            print(f"⏩ Review exists")
            continue

        Review.objects.create(
            client=client,
            professional_profile=profile,
            rating=random.randint(4, 5),
            comment=random.choice(review_comments),
        )

        print(f"✅ Review added")


print("\n🎉 Milestone 2 seed data completed successfully!\n")