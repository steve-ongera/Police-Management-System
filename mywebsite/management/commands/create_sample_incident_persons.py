from django.core.management.base import BaseCommand
from mywebsite.models import Incident, Person, IncidentPerson
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Create sample IncidentPerson records"

    def handle(self, *args, **kwargs):
        roles = ['suspect', 'victim', 'witness', 'complainant']
        total_links = 100
        created_count = 0

        incidents = list(Incident.objects.all())
        people = list(Person.objects.all())

        if not incidents or not people:
            self.stdout.write(self.style.ERROR("❌ No incidents or persons found. Please create those first."))
            return

        for _ in range(total_links):
            incident = random.choice(incidents)
            person = random.choice(people)
            role = random.choice(roles)

            # Avoid duplicates
            if IncidentPerson.objects.filter(incident=incident, person=person, role=role).exists():
                continue

            IncidentPerson.objects.create(
                incident=incident,
                person=person,
                role=role,
                statement=fake.paragraph(nb_sentences=3)
            )
            created_count += 1
            self.stdout.write(f"✅ Linked {person.full_name} as {role} to {incident.incident_number}")

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total IncidentPerson records created: {created_count}"))
