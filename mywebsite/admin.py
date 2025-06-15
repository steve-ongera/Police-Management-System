from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    User, Department, Station, CrimeType, Incident, Person, IncidentPerson,
    Evidence, Vehicle, IncidentVehicle, Report, Arrest, Equipment, Shift,
    EmergencyCall, CourtCase, AuditLog
)

# Custom Filters
class ActiveDutyFilter(SimpleListFilter):
    title = 'Active Duty Status'
    parameter_name = 'active_duty'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active Duty'),
            ('inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active_duty=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active_duty=False)

class IncidentStatusFilter(SimpleListFilter):
    title = 'Incident Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('open', 'Open Cases'),
            ('closed', 'Closed Cases'),
            ('recent', 'Recent (Last 7 days)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'open':
            return queryset.exclude(status__in=['resolved', 'closed'])
        if self.value() == 'closed':
            return queryset.filter(status__in=['resolved', 'closed'])
        if self.value() == 'recent':
            return queryset.filter(date_occurred__gte=timezone.now() - timedelta(days=7))

class PriorityFilter(SimpleListFilter):
    title = 'Priority Level'
    parameter_name = 'priority'

    def lookups(self, request, model_admin):
        return (
            ('high', 'High Priority (3-4)'),
            ('low', 'Low Priority (1-2)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'high':
            return queryset.filter(priority__gte=3)
        if self.value() == 'low':
            return queryset.filter(priority__lte=2)

# Custom Admin Classes
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'badge_number', 'full_name_display', 'role', 'is_active_duty', 'date_joined_force', 'station_display')
    list_filter = ('role', ActiveDutyFilter, 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'badge_number', 'email')
    ordering = ('badge_number', 'last_name')
    list_per_page = 25
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Police Information', {
            'fields': ('role', 'badge_number', 'phone_number', 'address', 'date_joined_force', 'is_active_duty')
        }),
    )
    
    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name_display.short_description = 'Full Name'
    
    def station_display(self, obj):
        try:
            station = Station.objects.filter(station_commander=obj).first()
            if station:
                return station.name
            return '-'
        except:
            return '-'
    station_display.short_description = 'Station'

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head_officer', 'contact_number', 'station_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at',)
    
    def station_count(self, obj):
        return obj.station_set.count()
    station_count.short_description = 'Number of Stations'

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'station_commander', 'phone_number', 'is_active', 'incident_count')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'code', 'address')
    list_editable = ('is_active',)
    
    def incident_count(self, obj):
        count = obj.incident_set.count()
        url = reverse('admin:your_app_incident_changelist') + f'?station__id__exact={obj.id}'
        return format_html('<a href="{}">{} incidents</a>', url, count)
    incident_count.short_description = 'Incidents'

@admin.register(CrimeType)
class CrimeTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'severity_level', 'incident_count')
    list_filter = ('category', 'severity_level')
    search_fields = ('name', 'code', 'description')
    ordering = ('severity_level', 'code')
    
    def incident_count(self, obj):
        return obj.incident_set.count()
    incident_count.short_description = 'Total Incidents'

class IncidentPersonInline(admin.TabularInline):
    model = IncidentPerson
    extra = 1
    autocomplete_fields = ['person']

class IncidentVehicleInline(admin.TabularInline):
    model = IncidentVehicle
    extra = 1
    autocomplete_fields = ['vehicle']

class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0
    readonly_fields = ('evidence_id', 'created_at')
    fields = ('evidence_number', 'evidence_type', 'description', 'status', 'collected_by')

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_number', 'title', 'crime_type', 'status', 'priority_display', 'date_occurred', 'reporting_officer', 'station')
    list_filter = (IncidentStatusFilter, PriorityFilter, 'crime_type', 'station', 'date_occurred')
    search_fields = ('incident_number', 'title', 'description', 'location')
    readonly_fields = ('incident_id', 'date_reported', 'incident_number')
    list_editable = ('status',)
    date_hierarchy = 'date_occurred'
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('incident_id', 'incident_number', 'crime_type', 'title', 'description')
        }),
        ('Location & Time', {
            'fields': ('location', 'latitude', 'longitude', 'date_occurred', 'date_reported')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'is_active')
        }),
        ('Personnel', {
            'fields': ('reporting_officer', 'investigating_officer', 'station')
        }),
    )
    
    inlines = [IncidentPersonInline, IncidentVehicleInline, EvidenceInline]
    autocomplete_fields = ['reporting_officer', 'investigating_officer']
    
    def priority_display(self, obj):
        colors = {1: 'green', 2: 'orange', 3: 'red', 4: 'darkred'}
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.priority, 'black'),
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'crime_type', 'reporting_officer', 'investigating_officer', 'station'
        )

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'date_of_birth', 'phone_number', 'identification_number', 'incident_count')
    list_filter = ('gender', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email', 'identification_number')
    readonly_fields = ('person_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('person_id', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address', 'emergency_contact')
        }),
        ('Identification', {
            'fields': ('identification_number', 'occupation', 'photo')
        }),
        ('Notes & Timestamps', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def incident_count(self, obj):
        count = obj.incidentperson_set.count()
        return f"{count} incidents"
    incident_count.short_description = 'Incident Involvement'

@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('evidence_number', 'incident', 'evidence_type', 'status', 'collected_by', 'date_collected', 'storage_location')
    list_filter = ('evidence_type', 'status', 'date_collected')
    search_fields = ('evidence_number', 'description', 'location_found')
    readonly_fields = ('evidence_id', 'created_at')
    date_hierarchy = 'date_collected'
    
    fieldsets = (
        ('Identification', {
            'fields': ('evidence_id', 'evidence_number', 'incident', 'evidence_type')
        }),
        ('Details', {
            'fields': ('description', 'location_found', 'date_collected', 'collected_by')
        }),
        ('Status & Storage', {
            'fields': ('status', 'storage_location', 'file_attachment')
        }),
        ('Chain of Custody', {
            'fields': ('chain_of_custody', 'notes', 'created_at')
        }),
    )

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'make', 'model', 'year', 'color', 'owner_name', 'is_stolen')
    list_filter = ('make', 'year', 'is_stolen', 'created_at')
    search_fields = ('license_plate', 'vin', 'owner_name', 'make', 'model')
    list_editable = ('is_stolen',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            incident_count=Count('incidentvehicle')
        )

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_number', 'incident', 'report_type', 'title', 'created_by', 'is_finalized', 'date_created')
    list_filter = ('report_type', 'is_finalized', 'date_created')
    search_fields = ('report_number', 'title', 'content')
    readonly_fields = ('report_id', 'date_created')
    list_editable = ('is_finalized',)
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_id', 'report_number', 'incident', 'report_type', 'title')
        }),
        ('Content', {
            'fields': ('content', 'attachments')
        }),
        ('Review Process', {
            'fields': ('created_by', 'reviewed_by', 'date_created', 'date_reviewed', 'is_finalized')
        }),
    )

@admin.register(Arrest)
class ArrestAdmin(admin.ModelAdmin):
    list_display = ('arrest_number', 'person', 'arresting_officer', 'date_arrested', 'status', 'bail_amount', 'court_date')
    list_filter = ('status', 'date_arrested')
    search_fields = ('arrest_number', 'person__first_name', 'person__last_name', 'charges')
    readonly_fields = ('arrest_id', 'created_at')
    date_hierarchy = 'date_arrested'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('person', 'arresting_officer', 'incident')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('equipment_id', 'name', 'equipment_type', 'status', 'assigned_to', 'location', 'maintenance_due')
    list_filter = ('equipment_type', 'status', 'maintenance_due')
    search_fields = ('equipment_id', 'name', 'serial_number')
    list_editable = ('status', 'location')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assigned_to')

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('officer', 'shift_type', 'start_time', 'end_time', 'station', 'supervisor')
    list_filter = ('shift_type', 'start_time', 'station')
    search_fields = ('officer__first_name', 'officer__last_name', 'patrol_area')
    date_hierarchy = 'start_time'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('officer', 'station', 'supervisor')

@admin.register(EmergencyCall)
class EmergencyCallAdmin(admin.ModelAdmin):
    list_display = ('call_number', 'caller_name', 'priority_display', 'status', 'assigned_officer', 'time_received', 'response_time')
    list_filter = ('priority', 'status', 'time_received')
    search_fields = ('call_number', 'caller_name', 'caller_phone', 'description')
    readonly_fields = ('call_id', 'time_received')
    date_hierarchy = 'time_received'
    list_per_page = 25
    
    def priority_display(self, obj):
        colors = {1: 'green', 2: 'orange', 3: 'red', 4: 'darkred'}
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.priority, 'black'),
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    
    def response_time(self, obj):
        if obj.time_responded and obj.time_received:
            delta = obj.time_responded - obj.time_received
            return f"{delta.total_seconds()/60:.1f} min"
        return '-'
    response_time.short_description = 'Response Time'

@admin.register(CourtCase)
class CourtCaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'incident', 'court_name', 'status', 'filing_date', 'hearing_date')
    list_filter = ('status', 'court_name', 'filing_date')
    search_fields = ('case_number', 'judge_name', 'prosecutor', 'defense_attorney')
    date_hierarchy = 'filing_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('incident')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_repr', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'object_repr', 'ip_address')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'timestamp', 'ip_address')
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Admin Site Customization
admin.site.site_header = "Police Management System"
admin.site.site_title = "Police Admin"
admin.site.index_title = "Police Department Administration"

# Custom Dashboard Stats (Optional - would require additional setup)
class DashboardStats:
    @staticmethod
    def get_stats():
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        now = timezone.now()
        last_week = now - timedelta(days=7)
        
        stats = {
            'total_incidents': Incident.objects.count(),
            'open_incidents': Incident.objects.exclude(status__in=['resolved', 'closed']).count(),
            'recent_incidents': Incident.objects.filter(date_occurred__gte=last_week).count(),
            'total_arrests': Arrest.objects.count(),
            'active_officers': User.objects.filter(is_active_duty=True).count(),
            'evidence_items': Evidence.objects.count(),
            'emergency_calls_today': EmergencyCall.objects.filter(time_received__date=now.date()).count(),
        }
        return stats