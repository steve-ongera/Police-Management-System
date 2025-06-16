from django.core.management.base import BaseCommand
from mywebsite.models import Incident, Vehicle, IncidentVehicle
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Create sample incident-vehicle relationships"

    def handle(self, *args, **kwargs):
        INVOLVEMENT_TYPES = [
            'stolen', 'damaged', 'used_in_crime', 'abandoned', 'confiscated', 'involved_in_accident'
        ]

        incidents = list(Incident.objects.all())
        vehicles = list(Vehicle.objects.all())

        if not incidents or not vehicles:
            self.stdout.write(self.style.ERROR("❌ You need existing incidents and vehicles to create relationships."))
            return

        count = 0
        for _ in range(100):  # Number of links to create
            incident = random.choice(incidents)
            vehicle = random.choice(vehicles)
            involvement_type = random.choice(INVOLVEMENT_TYPES)
            description = fake.sentence(nb_words=10)

            # Avoid duplicates
            if IncidentVehicle.objects.filter(incident=incident, vehicle=vehicle, involvement_type=involvement_type).exists():
                continue

            IncidentVehicle.objects.create(
                incident=incident,
                vehicle=vehicle,
                involvement_type=involvement_type,
                description=description
            )
            count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Linked vehicle {vehicle.license_plate} to incident {incident.id} as {involvement_type}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total incident-vehicle records created: {count}"))
