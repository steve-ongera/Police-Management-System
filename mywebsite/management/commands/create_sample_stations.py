from django.core.management.base import BaseCommand
from mywebsite.models import Station, Department, User
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Create at least 50 police stations with one per county"

    def handle(self, *args, **kwargs):
        counties = [
            "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Uasin Gishu", "Kiambu", "Machakos",
            "Meru", "Tharaka-Nithi", "Embu", "Kirinyaga", "Nyeri", "Murang'a", "Laikipia",
            "Turkana", "West Pokot", "Samburu", "Trans Nzoia", "Elgeyo Marakwet", "Nandi",
            "Baringo", "Bomet", "Kericho", "Narok", "Kajiado", "Homa Bay", "Migori", "Kisii",
            "Nyamira", "Siaya", "Busia", "Vihiga", "Kakamega", "Bungoma", "Taita Taveta",
            "Kwale", "Kilifi", "Tana River", "Lamu", "Garissa", "Wajir", "Mandera", "Marsabit",
            "Isiolo", "Kitui", "Makueni", "Tana Delta"
        ]

        departments = list(Department.objects.all())
        commanders = list(User.objects.filter(role__in=['officer', 'supervisor', 'detective']))

        if len(departments) < 1 or len(commanders) < 1:
            self.stdout.write(self.style.ERROR("❌ Please ensure you have departments and eligible users."))
            return

        created_count = 0

        for i, county in enumerate(counties):
            station_name = f"{county} Police Station"
            code = f"STN-{i+1:03}"

            if Station.objects.filter(code=code).exists():
                continue

            station = Station.objects.create(
                name=station_name,
                code=code,
                department=random.choice(departments),
                address=fake.address(),
                phone_number=f"+2547{random.randint(10000000, 99999999)}",
                station_commander=random.choice(commanders),
                latitude=round(random.uniform(-4.7, 5.2), 6),
                longitude=round(random.uniform(33.5, 41.0), 6),
                is_active=random.choice([True, True, True, False])  # Most active
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Created station: {station.name}"))

        # Add a few more to ensure > 50
        extra = 5
        for i in range(extra):
            code = f"STN-X{i+1:02}"
            Station.objects.create(
                name=fake.city() + " Station",
                code=code,
                department=random.choice(departments),
                address=fake.address(),
                phone_number=f"+2547{random.randint(10000000, 99999999)}",
                station_commander=random.choice(commanders),
                latitude=round(random.uniform(-4.7, 5.2), 6),
                longitude=round(random.uniform(33.5, 41.0), 6),
                is_active=True
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Created {created_count} police stations successfully."))
