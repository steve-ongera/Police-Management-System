from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
import random
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample Kenyan police users'

    def handle(self, *args, **kwargs):
        first_names = [
            "Kevin", "Brian", "Derrick", "Collins", "Victor", "Elvis", "George", "Allan", "Daniel", "Mark",
            "Faith", "Jane", "Mercy", "Ann", "Lilian", "Cynthia", "Esther", "Agnes", "Winnie", "Beatrice"
        ]
        last_names = [
            "Mwangi", "Odhiambo", "Mutiso", "Otieno", "Kipchoge", "Njoroge", "Okello", "Wambui", "Chebet", "Kamau"
        ]
        roles = ['officer', 'detective', 'supervisor', 'dispatcher']

        for i in range(20):
            first = random.choice(first_names)
            last = random.choice(last_names)
            username = f"{first.lower()}.{last.lower()}{i}"
            email = f"{username}@police.go.ke"
            badge_number = f"KEP-{random.randint(10000, 99999)}"
            phone = f"+2547{random.randint(10000000, 99999999)}"
            role = random.choice(roles)
            address = f"{random.choice(['Nairobi', 'Mombasa', 'Kisumu', 'Eldoret', 'Nakuru'])}, Kenya"
            date_joined_force = timezone.now().date() - datetime.timedelta(days=random.randint(100, 3000))

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first,
                    last_name=last,
                    role=role,
                    badge_number=badge_number,
                    phone_number=phone,
                    address=address,
                    date_joined_force=date_joined_force,
                    is_active_duty=True,
                    password='police1234'  # default password
                )
                self.stdout.write(self.style.SUCCESS(f"Created user: {user}"))

        self.stdout.write(self.style.SUCCESS("✅ 20 Kenyan users created successfully."))
