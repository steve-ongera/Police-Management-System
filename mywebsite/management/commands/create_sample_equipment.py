from django.core.management.base import BaseCommand
from mywebsite.models import Equipment, User
import random
from faker import Faker
from datetime import timedelta
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = "Create sample equipment records"

    def handle(self, *args, **kwargs):
        EQUIPMENT_TYPES = ['weapon', 'vehicle', 'communication', 'protective', 'forensic', 'office']
        STATUS_CHOICES = ['available', 'assigned', 'maintenance', 'retired', 'lost']
        users = list(User.objects.all())

        if not users:
            self.stdout.write(self.style.WARNING("⚠ No users found. Some equipment may not be assigned."))

        total_created = 0

        for i in range(50):
            equipment_type = random.choice(EQUIPMENT_TYPES)
            status = random.choice(STATUS_CHOICES)
            assigned_user = random.choice(users) if status == 'assigned' and users else None

            equipment = Equipment.objects.create(
                equipment_id=f"EQ-{fake.unique.random_int(min=1000, max=9999)}",
                name=fake.word().capitalize() + " " + equipment_type.capitalize(),
                equipment_type=equipment_type,
                description=fake.text(max_nb_chars=100),
                serial_number=fake.bothify(text='SN-####-???'),
                purchase_date=fake.date_between(start_date='-5y', end_date='-30d'),
                purchase_cost=round(random.uniform(500, 10000), 2),
                assigned_to=assigned_user,
                status=status,
                location=fake.city(),
                maintenance_due=timezone.now().date() + timedelta(days=random.randint(30, 365)) if status == 'maintenance' else None,
                notes=fake.sentence()
            )

            total_created += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Created Equipment: {equipment.equipment_id} - {equipment.name}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total equipment records created: {total_created}"))
