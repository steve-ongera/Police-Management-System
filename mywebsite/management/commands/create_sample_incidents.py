from django.core.management.base import BaseCommand
from django.utils import timezone
from mywebsite.models import Incident, User, CrimeType, Station
import random
import uuid
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Create sample incident records"

    def handle(self, *args, **kwargs):
        officers = User.objects.filter(role='officer')
        crime_types = list(CrimeType.objects.all())
        stations = list(Station.objects.all())

        if not officers.exists() or not crime_types or not stations:
            self.stdout.write(self.style.ERROR("🚫 Ensure users (officers), stations, and crime types exist before running this script."))
            return

        total_to_create = 50
        created_count = 0

        for _ in range(total_to_create):
            station = random.choice(stations)
            reporting_officer = random.choice(officers)
            investigating_officer = random.choice(officers)
            crime_type = random.choice(crime_types)

            date_occurred = fake.date_time_between(start_date='-6M', end_date='now')
            incident_number = f"INC{random.randint(100000, 999999)}"

            # Ensure unique incident_number
            if Incident.objects.filter(incident_number=incident_number).exists():
                continue

            incident = Incident.objects.create(
                incident_id=uuid.uuid4(),
                incident_number=incident_number,
                crime_type=crime_type,
                title=fake.sentence(nb_words=6),
                description=fake.paragraph(nb_sentences=3),
                date_occurred=date_occurred,
                location=fake.address(),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude()),
                status=random.choice(['reported', 'investigating', 'resolved', 'closed', 'pending']),
                reporting_officer=reporting_officer,
                investigating_officer=investigating_officer,
                station=station,
                priority=random.choice([1, 2, 3, 4]),
                is_active=random.choice([True, True, False])  # More likely to be active
            )

            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Incident Created: {incident.incident_number} - {incident.title}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total incidents created: {created_count}"))
