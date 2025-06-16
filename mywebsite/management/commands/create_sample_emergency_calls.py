import random
import uuid
from datetime import timedelta, timezone as dt_timezone  # <-- Fix here
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from mywebsite.models import EmergencyCall, Incident
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = "Generate sample emergency calls"

    def handle(self, *args, **kwargs):
        users = list(User.objects.all())
        incidents = list(Incident.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("❌ No users found. Please create users first."))
            return

        for _ in range(20):  # Generate 20 sample calls
            call_number = f"CALL-{uuid.uuid4().hex[:8].upper()}"
            caller_name = fake.name()
            caller_phone = fake.phone_number()[:15]
            location = fake.address()
            description = fake.sentence(nb_words=12)
            priority = random.randint(1, 4)
            status = random.choice(['received', 'dispatched', 'responded', 'completed', 'cancelled'])

            received_by = random.choice(users)
            assigned_officer = random.choice(users) if random.random() > 0.3 else None
            incident = random.choice(incidents) if incidents and random.random() > 0.5 else None

            # Use timezone-aware datetime
            time_received = fake.date_time_between(start_date='-10d', end_date='now', tzinfo=dt_timezone.utc)
            time_dispatched = time_received + timedelta(minutes=random.randint(1, 30)) if status in ['dispatched', 'responded', 'completed'] else None
            time_responded = time_dispatched + timedelta(minutes=random.randint(5, 60)) if time_dispatched and status in ['responded', 'completed'] else None
            time_completed = time_responded + timedelta(minutes=random.randint(10, 120)) if time_responded and status == 'completed' else None

            call = EmergencyCall.objects.create(
                call_number=call_number,
                caller_name=caller_name,
                caller_phone=caller_phone,
                location=location,
                description=description,
                priority=priority,
                status=status,
                received_by=received_by,
                assigned_officer=assigned_officer,
                incident=incident,
                time_received=time_received,
                time_dispatched=time_dispatched,
                time_responded=time_responded,
                time_completed=time_completed,
                notes=fake.paragraph(nb_sentences=2)
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Created Emergency Call: {call}"))
