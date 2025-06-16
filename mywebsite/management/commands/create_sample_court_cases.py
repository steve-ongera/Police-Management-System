import random
import uuid
from datetime import timedelta, datetime, timezone as dt_timezone
from django.core.management.base import BaseCommand
from faker import Faker
from mywebsite.models import CourtCase, Incident

fake = Faker()

class Command(BaseCommand):
    help = "Generate sample court cases"

    def handle(self, *args, **kwargs):
        incidents = list(Incident.objects.all())

        if not incidents:
            self.stdout.write(self.style.ERROR("❌ No incidents found. Please create some first."))
            return

        for _ in range(20):  # Generate 20 court cases
            case_number = f"CASE-{uuid.uuid4().hex[:8].upper()}"
            incident = random.choice(incidents)
            court_name = f"{fake.city()} District Court"
            judge_name = fake.name()
            prosecutor = fake.name()
            defense_attorney = fake.name()
            
            # Filing date within last 90 days
            filing_date = fake.date_between(start_date='-90d', end_date='today')

            # Hearing date: optional, in future, 50% chance
            hearing_date = (
                fake.date_time_between(start_date='now', end_date='+30d', tzinfo=dt_timezone.utc)
                if random.random() > 0.5 else None
            )

            status = random.choice(['pending', 'active', 'closed', 'dismissed', 'settled'])

            verdict = fake.sentence(nb_words=10) if status in ['closed', 'dismissed', 'settled'] else ''
            sentence = fake.paragraph(nb_sentences=2) if status == 'closed' else ''
            notes = fake.paragraph(nb_sentences=2)

            court_case = CourtCase.objects.create(
                case_number=case_number,
                incident=incident,
                court_name=court_name,
                judge_name=judge_name,
                prosecutor=prosecutor,
                defense_attorney=defense_attorney,
                filing_date=filing_date,
                hearing_date=hearing_date,
                status=status,
                verdict=verdict,
                sentence=sentence,
                notes=notes,
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Created Court Case: {court_case}"))
