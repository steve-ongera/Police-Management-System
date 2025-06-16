from django.core.management.base import BaseCommand
from mywebsite.models import Vehicle
from faker import Faker
import random
import string
from datetime import datetime, timedelta

fake = Faker()

class Command(BaseCommand):
    help = "Create sample Vehicle records"

    def handle(self, *args, **kwargs):
        makes_models = {
            "Toyota": ["Corolla", "Camry", "RAV4"],
            "Honda": ["Civic", "Accord", "CR-V"],
            "Ford": ["Focus", "Fusion", "Escape"],
            "Nissan": ["Altima", "Sentra", "Rogue"],
            "Mazda": ["3", "6", "CX-5"]
        }

        colors = ["Red", "Blue", "Black", "White", "Silver", "Green", "Gray"]
        created_count = 0

        for _ in range(100):
            make = random.choice(list(makes_models.keys()))
            model = random.choice(makes_models[make])
            year = random.randint(2005, datetime.now().year)
            color = random.choice(colors)
            license_plate = f"{''.join(random.choices(string.ascii_uppercase, k=3))} {random.randint(1000, 9999)}"
            vin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=17))
            owner_name = fake.name()
            owner_phone = fake.phone_number()[:15]
            owner_address = fake.address()
            registration_date = fake.date_between(start_date='-10y', end_date='today')
            insurance_info = fake.company() + " Insurance"
            is_stolen = random.choice([False, False, False, True])  # Mostly not stolen

            vehicle = Vehicle.objects.create(
                license_plate=license_plate,
                make=make,
                model=model,
                year=year,
                color=color,
                vin=vin,
                owner_name=owner_name,
                owner_phone=owner_phone,
                owner_address=owner_address,
                registration_date=registration_date,
                insurance_info=insurance_info,
                is_stolen=is_stolen,
                notes=fake.sentence()
            )

            created_count += 1
            self.stdout.write(f"✅ Created: {vehicle.license_plate} ({vehicle.make} {vehicle.model})")

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total vehicles created: {created_count}"))
