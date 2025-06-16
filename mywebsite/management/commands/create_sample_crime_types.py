from django.core.management.base import BaseCommand
from mywebsite.models import CrimeType
import random

class Command(BaseCommand):
    help = "Create sample crime types"

    def handle(self, *args, **kwargs):
        crime_types = [
            ("Theft", "THEFT", "Property Crime", 2, "Unlawful taking of property."),
            ("Burglary", "BURGLARY", "Property Crime", 3, "Illegal entry into a building with intent to commit a crime."),
            ("Assault", "ASSAULT", "Violent Crime", 3, "Physical attack on another person."),
            ("Homicide", "HOMICIDE", "Violent Crime", 4, "Unlawful killing of another human."),
            ("Drug Possession", "DRUG_POS", "Drug Offense", 2, "Illegal possession of controlled substances."),
            ("Drug Trafficking", "DRUG_TRAFF", "Drug Offense", 4, "Distribution and sale of illegal drugs."),
            ("Corruption", "CORRUPT", "White Collar Crime", 3, "Misuse of power for personal gain."),
            ("Cybercrime", "CYBER", "Technology Crime", 3, "Crimes committed via digital systems."),
            ("Fraud", "FRAUD", "White Collar Crime", 2, "Intentional deception for gain."),
            ("Domestic Violence", "DOM_VIOL", "Violent Crime", 3, "Violence within domestic settings."),
            ("Traffic Violation", "TRAFFIC", "Public Safety", 1, "Breaking traffic laws."),
            ("Robbery", "ROBBERY", "Violent Crime", 3, "Theft involving threat or force."),
            ("Arson", "ARSON", "Property Crime", 3, "Intentional setting of fires."),
            ("Kidnapping", "KIDNAP", "Violent Crime", 4, "Unlawful confinement or abduction."),
            ("Bribery", "BRIBERY", "White Collar Crime", 2, "Offering something of value to influence."),
            ("Vandalism", "VANDAL", "Property Crime", 2, "Intentional destruction of property."),
            ("Human Trafficking", "HUM_TRAFF", "Organized Crime", 4, "Illegal trade of people."),
            ("Money Laundering", "LAUNDER", "White Collar Crime", 3, "Concealing illicit funds."),
            ("Trespassing", "TRESPASS", "Public Order", 1, "Unauthorized entry into premises."),
            ("Extortion", "EXTORT", "Organized Crime", 3, "Obtaining things through threats."),
        ]

        created = 0
        for name, code, category, severity, desc in crime_types:
            if not CrimeType.objects.filter(code=code).exists():
                CrimeType.objects.create(
                    name=name,
                    code=code,
                    category=category,
                    severity_level=severity,
                    description=desc
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {code} - {name}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 {created} crime types created successfully."))
