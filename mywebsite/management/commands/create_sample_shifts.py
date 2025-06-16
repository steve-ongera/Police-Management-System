from django.core.management.base import BaseCommand
from mywebsite.models import Shift, User, Station
import random
from faker import Faker
from datetime import timedelta, datetime
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = "Create sample shift records"

    def handle(self, *args, **kwargs):
        SHIFT_TYPES = ['day', 'evening', 'night', 'overtime']
        users = list(User.objects.all())
        stations = list(Station.objects.all())

        if not users:
            self.stdout.write(self.style.WARNING("⚠ No officers found. Cannot create shifts without users."))
            return

        if not stations:
            self.stdout.write(self.style.WARNING("⚠ No stations found. Cannot create shifts without stations."))
            return

        total_created = 0

        for _ in range(50):
            officer = random.choice(users)
            supervisor = random.choice(users) if random.random() > 0.3 else None
            station = random.choice(stations)
            shift_type = random.choice(SHIFT_TYPES)

            # Simulate realistic time ranges
            base_date = timezone.now().date() - timedelta(days=random.randint(0, 60))
            if shift_type == 'day':
                start_time = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=8)
                end_time = start_time + timedelta(hours=8)
            elif shift_type == 'evening':
                start_time = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=16)
                end_time = start_time + timedelta(hours=8)
            elif shift_type == 'night':
                start_time = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=22)
                end_time = start_time + timedelta(hours=8)
            else:  # overtime
                start_time = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=random.randint(8, 20))
                end_time = start_time + timedelta(hours=random.randint(2, 6))

            shift = Shift.objects.create(
                officer=officer,
                shift_type=shift_type,
                start_time=start_time,
                end_time=end_time,
                station=station,
                patrol_area=fake.city(),
                supervisor=supervisor if supervisor != officer else None,
                notes=fake.sentence(nb_words=10),
            )

            total_created += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Created Shift: {shift}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total shifts created: {total_created}"))
