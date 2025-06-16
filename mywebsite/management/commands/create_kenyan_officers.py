import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker()  # Default locale (en_US)

class Command(BaseCommand):
    help = "Generate 300 Kenyan police officers with password 'police123'"

    def handle(self, *args, **kwargs):
        password = "police123"
        created = 0

        for _ in range(300):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}"
            email = f"{username}@police.go.ke"
            badge_number = f"KEP-{random.randint(100000, 999999)}"
            phone_number = f"+2547{random.randint(10000000, 99999999)}"  # Kenyan mobile format
            address = fake.street_address() + ", Kenya"
            date_joined_force = fake.date_between(start_date='-10y', end_date='-1y')

            if User.objects.filter(username=username).exists() or User.objects.filter(badge_number=badge_number).exists():
                continue  # skip duplicates

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='officer',
                badge_number=badge_number,
                phone_number=phone_number,
                address=address,
                date_joined_force=date_joined_force,
                is_active_duty=True,
            )
            user.set_password(password)
            user.save()
            created += 1

            self.stdout.write(self.style.SUCCESS(f"✅ Created Officer {created}: {user}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully created {created} Kenyan police officers."))
