import os
import django
import uuid
from django.core.exceptions import ObjectDoesNotExist


# Initialize Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_swalook.settings")
django.setup()
from _api_.models import VendorService, VendorServiceCategory, SalonBranch, User
# Define default user
USER_PHONE = "6001844177"  # Change if needed

try:
    user = User.objects.get(username=USER_PHONE)
    branch = SalonBranch.objects.get(vendor_name=user)
   
except ObjectDoesNotExist:
    print("User or Branch not found. Ensure they exist before running the script.")
    exit()
data = {
    "Growing": {
        "Haircut": 400,
        "Beard Styling": 200,
        "Lightening White Top Up Mask": 400,
        "Blow Dry and Setting": 200,
        "Child Haircut (Below 12)": 300
    },
    "Hair Colour": {
        "Per Foil": 200,
        "Sidelocks Colour": 500,
        "Sidelocks Colour Men (AF)": 600,
        "Global Colour": 1200,
        "Root Touch-Up Up to Two Inch Colour (AF)": 1200,
        "Root Touch-Up Up to Two Inch Colour": 1400,
        "Global Ammonia Free": 1500,
        "Global Highlights (Length Dependent)": 1500,
        "Partial": 3000
    },
    "Pre-Lightening": {
        "Pre-Lightening": 500
    },
    "Hair Training": {
        "Straightening (Short)": 2500,
        "Smoothering (Short)": 2500,
        "Straightening (Long)": 3000,
        "Smoothering (Long)": 3000,
        "Keratin Treatment (Short)": 3200,
        "Keratin Treatment (Long)": 3600
    },
    "Wash & Dry": {
        "Wash & Plain Dry": 250,
        "Wash & Blow Dry": 300
    },
    "Spa Treatments": {
        "Insta Care Spa": 500,
        "Streax Spa": 750,
        "Destress Spa": 880,
        "L'Oréal Spa": 900,
        "Protein Rush": 1100,
        "Dandruff Treatment": 1500,
        "Iluvia Argan Detox Spa": 1600,
        "Moroccanoli Spa": 1700
    },
    "Clean Up": {
        "Regular Clean Up": 500,
        "Lotus Clean Up": 700,
        "Fruits Clean Up": 1100
    },
    "Treatment": {
        "Anti Acne Treatment": 1650
    },
    "Detan": {
        "Lotus Detan Feet": 300,
        "Lotus Detan F&N": 450,
        "Lotus Detan Half Arms": 600,
        "Lotus Detan Full Arms": 900
    },
    "Facial": {
        "Lotus Regular Facial": 1200,
        "Kanpeki Tan Removal Facial": 1300,
        "Fruits Facial": 1600,
        "Insta Vita C Facial": 2200,
        "Hydrating Facial": 2400,
        "Radiant Illuminate Facial": 2600,
        "Youth Infinity Facial": 3000,
        "Kanpeki Papaya & Marshmallow": 4500,
        "Kanpeki Ginger & Walnut": 4500,
        "Kanpeki Jamaican Sorrel": 4500
    },
    "Pedicure": {
        "Orchid Next Pedicure": 950,
        "Lotus Pedicure": 1000,
        "White Tea Vitality Pedicure": 1500,
        "Kanpeki Pedipie Pedicure": 1500,
        "Chocolate Pedicure": 1500,
        "Signature Pedicure": 1700,
        "Cappuccino Pedicure": 2100,
        "Kanpeki Crystal Pedicure": 2100
    },
    "Piercing": {
        "Piercing": 200
    }
}


# Insert services into the database
for category_name, services in data.items():
    category, _ = VendorServiceCategory.objects.get_or_create(service_category=category_name,user=user,vendor_branch=branch)
    
    for service_name, service_price in services.items():
        if isinstance(service_price, dict):  # Handle nested price structures
            for sub_service_name, sub_service_price in service_price.items():
                VendorService.objects.create(
                    id=uuid.uuid4(),
                    user=user,
                    category=category,
                    service=f"{service_name} - {sub_service_name}",
                    service_price=sub_service_price,
                    service_duration="",
                    for_men=True,  # Adjust gender filters if needed
                    for_women=False,
                    vendor_branch=branch
                )
        else:
            VendorService.objects.create(
                id=uuid.uuid4(),
                user=user,
                category=category,
                service=service_name,
                service_price=service_price,
                service_duration="",
                for_men=True,
                for_women=False,
                vendor_branch=branch
            )

print("Services inserted successfully.")
