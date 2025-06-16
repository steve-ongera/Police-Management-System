from django.core.management.base import BaseCommand
from mywebsite.models import Report, Incident, User
import random
import uuid
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Create sample report records"

    def handle(self, *args, **kwargs):
        REPORT_TYPES = [
            'incident', 'investigation', 'arrest',
            'traffic', 'patrol', 'evidence',
        ]

        incidents = list(Incident.objects.all())
        users = list(User.objects.all())

        if not incidents or not users:
            self.stdout.write(self.style.ERROR("❌ Need existing Incident and User records to generate reports."))
            return

        count = 0
        for _ in range(100):
            incident = random.choice(incidents)
            created_by = random.choice(users)
            reviewed_by = random.choice(users) if random.choice([True, False]) else None

            report_type = random.choice(REPORT_TYPES)
            title = fake.sentence(nb_words=6)
            content = fake.paragraph(nb_sentences=10)

            report = Report.objects.create(
                report_id=uuid.uuid4(),
                report_number=f"RPT-{random.randint(100000, 999999)}",
                incident=incident,
                report_type=report_type,
                title=title,
                content=content,
                created_by=created_by,
                reviewed_by=reviewed_by,
                is_finalized=random.choice([True, False]),
                date_reviewed=fake.date_time_between(start_date="-30d", end_date="now") if reviewed_by else None
            )

            count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Created Report: {report.report_number} ({report.report_type})"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total reports created: {count}"))
