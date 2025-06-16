from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('officer', 'Police Officer'),
        ('detective', 'Detective'),
        ('supervisor', 'Supervisor'),
        ('dispatcher', 'Dispatcher'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='officer')
    badge_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_joined_force = models.DateField(null=True, blank=True)
    is_active_duty = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.badge_number})"

# Department and Station Management
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Station(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    station_commander = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.code}"

# Crime and Incident Management
class CrimeType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=50)
    severity_level = models.IntegerField(choices=[(1, 'Minor'), (2, 'Moderate'), (3, 'Serious'), (4, 'Critical')])
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Incident(models.Model):
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]
    
    incident_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    incident_number = models.CharField(max_length=20, unique=True)
    crime_type = models.ForeignKey(CrimeType, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_occurred = models.DateTimeField()
    date_reported = models.DateTimeField(auto_now_add=True)
    location = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    reporting_officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    investigating_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='investigating_incidents')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    priority = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')], default=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.incident_number} - {self.title}"

    class Meta:
        ordering = ['-date_occurred']

# Person Management (Suspects, Victims, Witnesses)
class Person(models.Model):
    PERSON_TYPE_CHOICES = [
        ('suspect', 'Suspect'),
        ('victim', 'Victim'),
        ('witness', 'Witness'),
        ('complainant', 'Complainant'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Unknown'),
    ]
    
    person_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    identification_number = models.CharField(max_length=50, blank=True)  # ID card, passport, etc.
    occupation = models.CharField(max_length=100, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='person_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()

class IncidentPerson(models.Model):
    """Junction table for many-to-many relationship between Incident and Person"""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Person.PERSON_TYPE_CHOICES)
    statement = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('incident', 'person', 'role')

# Evidence Management
class Evidence(models.Model):
    EVIDENCE_TYPE_CHOICES = [
        ('physical', 'Physical Evidence'),
        ('digital', 'Digital Evidence'),
        ('document', 'Document'),
        ('photograph', 'Photograph'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('biological', 'Biological Sample'),
    ]
    
    STATUS_CHOICES = [
        ('collected', 'Collected'),
        ('analyzed', 'Analyzed'),
        ('stored', 'In Storage'),
        ('returned', 'Returned'),
        ('destroyed', 'Destroyed'),
    ]
    
    evidence_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    evidence_number = models.CharField(max_length=50, unique=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='evidences')
    evidence_type = models.CharField(max_length=20, choices=EVIDENCE_TYPE_CHOICES)
    description = models.TextField()
    location_found = models.TextField()
    date_collected = models.DateTimeField()
    collected_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='collected')
    storage_location = models.CharField(max_length=100)
    chain_of_custody = models.TextField()
    file_attachment = models.FileField(upload_to='evidence_files/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.evidence_number} - {self.description[:50]}"

# Vehicle Management
class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    color = models.CharField(max_length=30)
    vin = models.CharField(max_length=17, unique=True, blank=True)
    owner_name = models.CharField(max_length=100)
    owner_phone = models.CharField(max_length=15, blank=True)
    owner_address = models.TextField(blank=True)
    registration_date = models.DateField(null=True, blank=True)
    insurance_info = models.TextField(blank=True)
    is_stolen = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.license_plate} - {self.make} {self.model}"

class IncidentVehicle(models.Model):
    """Junction table for incidents involving vehicles"""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    involvement_type = models.CharField(max_length=50)  # 'stolen', 'damaged', 'used_in_crime', etc.
    description = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

# Report Management
class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('incident', 'Incident Report'),
        ('investigation', 'Investigation Report'),
        ('arrest', 'Arrest Report'),
        ('traffic', 'Traffic Report'),
        ('patrol', 'Patrol Report'),
        ('evidence', 'Evidence Report'),
    ]
    
    report_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    report_number = models.CharField(max_length=50, unique=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    date_created = models.DateTimeField(auto_now_add=True)
    date_reviewed = models.DateTimeField(null=True, blank=True)
    is_finalized = models.BooleanField(default=False)
    attachments = models.FileField(upload_to='report_attachments/', null=True, blank=True)

    def __str__(self):
        return f"{self.report_number} - {self.title}"

# Arrest Management
class Arrest(models.Model):
    STATUS_CHOICES = [
        ('arrested', 'Arrested'),
        ('released', 'Released'),
        ('charged', 'Charged'),
        ('bail', 'Released on Bail'),
        ('transferred', 'Transferred'),
    ]
    
    arrest_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    arrest_number = models.CharField(max_length=50, unique=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='arrests')
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    arresting_officer = models.ForeignKey(User, on_delete=models.CASCADE)
    date_arrested = models.DateTimeField()
    location = models.TextField()
    charges = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='arrested')
    bail_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    court_date = models.DateTimeField(null=True, blank=True)
    release_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.arrest_number} - {self.person.full_name}"

# Equipment and Asset Management
class Equipment(models.Model):
    EQUIPMENT_TYPE_CHOICES = [
        ('weapon', 'Weapon'),
        ('vehicle', 'Police Vehicle'),
        ('communication', 'Communication Device'),
        ('protective', 'Protective Gear'),
        ('forensic', 'Forensic Equipment'),
        ('office', 'Office Equipment'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('lost', 'Lost/Stolen'),
    ]
    
    equipment_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.CharField(max_length=100)
    maintenance_due = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipment_id} - {self.name}"

# Shift and Duty Management
class Shift(models.Model):
    SHIFT_TYPE_CHOICES = [
        ('day', 'Day Shift'),
        ('evening', 'Evening Shift'),
        ('night', 'Night Shift'),
        ('overtime', 'Overtime'),
    ]
    
    officer = models.ForeignKey(User, on_delete=models.CASCADE)
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    patrol_area = models.CharField(max_length=100, blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_shifts')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
       return f"{self.officer.get_full_name()} - {self.shift_type} ({self.start_time.date()})"


# Emergency Call Management
class EmergencyCall(models.Model):
    PRIORITY_CHOICES = [
        (1, 'Low Priority'),
        (2, 'Medium Priority'),
        (3, 'High Priority'),
        (4, 'Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('dispatched', 'Dispatched'),
        ('responded', 'Responded'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    call_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    call_number = models.CharField(max_length=50, unique=True)
    caller_name = models.CharField(max_length=100, blank=True)
    caller_phone = models.CharField(max_length=15)
    location = models.TextField()
    description = models.TextField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    received_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_calls')
    assigned_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_calls')
    time_received = models.DateTimeField(auto_now_add=True)
    time_dispatched = models.DateTimeField(null=True, blank=True)
    time_responded = models.DateTimeField(null=True, blank=True)
    time_completed = models.DateTimeField(null=True, blank=True)
    incident = models.OneToOneField(Incident, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.call_number} - {self.description[:50]}"

# Court Case Management
class CourtCase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('dismissed', 'Dismissed'),
        ('settled', 'Settled'),
    ]
    
    case_number = models.CharField(max_length=50, unique=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    court_name = models.CharField(max_length=100)
    judge_name = models.CharField(max_length=100, blank=True)
    prosecutor = models.CharField(max_length=100, blank=True)
    defense_attorney = models.CharField(max_length=100, blank=True)
    filing_date = models.DateField()
    hearing_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verdict = models.TextField(blank=True)
    sentence = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case_number} - {self.court_name}"

# Audit Trail
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=200)
    changes = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} {self.action} {self.model_name} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']