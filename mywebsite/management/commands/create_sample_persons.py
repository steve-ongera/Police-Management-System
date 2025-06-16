from django.core.management.base import BaseCommand
from mywebsite.models import Person
import random
import uuid
from faker import Faker

fake = Faker('en_US')

class Command(BaseCommand):
    help = "Create sample person records"

    def handle(self, *args, **kwargs):
        PERSON_TYPES = ['suspect', 'victim', 'witness', 'complainant']
        GENDERS = ['M', 'F', 'O', 'U']
        OCCUPATIONS = ['Farmer', 'Teacher', 'Engineer', 'Student', 'Trader', 'Driver', 'Doctor', 'Police Officer']

        total_to_create = 100
        created_count = 0

        for _ in range(total_to_create):
            gender = random.choice(GENDERS)
            first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()
            last_name = fake.last_name()
            middle_name = fake.first_name() if random.choice([True, False]) else ''

            person = Person.objects.create(
                person_id=uuid.uuid4(),
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
                gender=gender,
                phone_number=fake.phone_number()[:15],
                email=fake.email(),
                address=fake.address(),
                identification_number=str(fake.random_int(min=10000000, max=99999999))[:50],
                occupation=random.choice(OCCUPATIONS),
                emergency_contact=fake.phone_number()[:100],
                notes=fake.text(max_nb_chars=150),
            )

            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Created: {person.full_name} ({person.gender})"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Total persons created: {created_count}"))
