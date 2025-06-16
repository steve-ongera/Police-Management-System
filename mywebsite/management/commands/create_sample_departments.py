from django.core.management.base import BaseCommand
from mywebsite.models import Department, User
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Generate sample departments with Kenyan-style data"

    def handle(self, *args, **kwargs):
        department_names = [
            "Criminal Investigation", "Traffic", "Cyber Crime", "Forensics",
            "Anti-Terrorism", "Narcotics", "Public Safety", "Internal Affairs",
            "Border Patrol", "Community Policing"
        ]

        created_count = 0

        available_heads = list(User.objects.filter(role__in=['supervisor', 'officer']))

        if not available_heads:
            self.stdout.write(self.style.ERROR("⚠️ No users with suitable roles found. Create some users first."))
            return

        for i, name in enumerate(department_names):
            code = f"DEP-{i+1:03}"
            if Department.objects.filter(code=code).exists():
                continue

            # Kenyan-style phone number
            phone = f"+2547{random.randint(10000000, 99999999)}"

            department = Department.objects.create(
                name=name,
                code=code,
                description=fake.paragraph(nb_sentences=2),
                head_officer=random.choice(available_heads),
                contact_number=phone,
                email=f"{name.lower().replace(' ', '')}@police.go.ke"
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Created department: {department.name}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully created {created_count} departments."))
