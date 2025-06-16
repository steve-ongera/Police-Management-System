from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mywebsite.models import Evidence, Incident
import random
import uuid
from faker import Faker
from datetime import timedelta
from django.utils import timezone

fake = Faker()

User = get_user_model()

class Command(BaseCommand):
    help = "Create sample Evidence records"

    def handle(self, *args, **kwargs):
        evidence_types = ['physical', 'digital', 'document', 'photograph', 'video', 'audio', 'biological']
        status_choices = ['collected', 'analyzed', 'stored', 'returned', 'destroyed']
        created_count = 0

        incidents = list(Incident.objects.all())
        users = list(User.objects.all())

        if not incidents or not users:
            self.stdout.write(self.style.ERROR("❌ No incidents or users found. Make sure you have them in the database."))
            return

        for _ in range(100):
            incident = random.choice(incidents)
            collected_by = random.choice(users)
            evidence_type = random.choice(evidence_types)
            status = random.choice(status_choices)
            date_collected = incident.date_occurred + timedelta(hours=random.randint(1, 72))

            evidence = Evidence.objects.create(
                evidence_id=uuid.uuid4(),
                evidence_number=f"EV{random.randint(100000, 999999)}",
                incident=incident,
                evidence_type=evidence_type,
                description=fake.text(max_nb_chars=150),
                location_found=fake.address(),
                date_collected=date_collected,
                collected_by=collected_by,
                status=status,
                storage_location=f"Storage Room {random.randint(1, 10)} - Shelf {random.choice('ABC')}{random.randint(1, 5)}",
                chain_of_custody=f"Collected by {collected_by.get_full_name()} on {date_collected.strftime('%Y-%m-%d %H:%M')}",
                notes=fake.sentence(nb_words=10)
            )

            created_count += 1
            self.stdout.write(f"✅ Created Evidence: {evidence.evidence_number} for Incident {incident.incident_number}")

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total Evidence records created: {created_count}"))
