from django.core.management.base import BaseCommand
from mywebsite.models import Arrest, Person, Incident, User
import random
import uuid
from faker import Faker
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = "Create sample arrest records"

    def handle(self, *args, **kwargs):
        STATUS_CHOICES = ['arrested', 'released', 'charged', 'bail', 'transferred']

        persons = list(Person.objects.all())
        incidents = list(Incident.objects.all())
        users = list(User.objects.all())

        if not persons or not incidents or not users:
            self.stdout.write(self.style.ERROR("❌ Make sure Person, Incident, and User records exist."))
            return

        total_created = 0

        for _ in range(50):
            person = random.choice(persons)
            incident = random.choice(incidents)
            officer = random.choice(users)

            status = random.choice(STATUS_CHOICES)
            bail_amount = round(random.uniform(1000, 10000), 2) if status == 'bail' else None
            release_date = fake.date_time_between(start_date="-5d", end_date="now") if status in ['released', 'bail', 'transferred'] else None
            court_date = fake.date_time_between(start_date="now", end_date="+30d") if status in ['charged', 'bail'] else None

            arrest = Arrest.objects.create(
                arrest_id=uuid.uuid4(),
                arrest_number=f"AR-{random.randint(10000, 99999)}",
                incident=incident,
                person=person,
                arresting_officer=officer,
                date_arrested=fake.date_time_between(start_date="-60d", end_date="-1d"),
                location=fake.address(),
                charges=fake.sentence(nb_words=6),
                status=status,
                bail_amount=bail_amount,
                court_date=court_date,
                release_date=release_date,
                notes=fake.paragraph(nb_sentences=3)
            )

            total_created += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Created Arrest: {arrest.arrest_number} for {person.full_name}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total arrests created: {total_created}"))
