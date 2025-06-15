from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import (
    User, Incident, Evidence, EmergencyCall, Arrest, 
    Person, Vehicle, Equipment, Shift, Department, Station
)

def login_view(request):
    """
    Handle user login with role-based redirection
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        if username and password:
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Set session expiry based on remember me
                    if not remember_me:
                        request.session.set_expiry(0)  # Session expires when browser closes
                    else:
                        request.session.set_expiry(1209600)  # 2 weeks
                    
                    # Role-based welcome message
                    role_messages = {
                        'admin': 'Welcome back, Administrator!',
                        'supervisor': 'Welcome back, Supervisor!',
                        'detective': 'Welcome back, Detective!',
                        'officer': 'Welcome back, Officer!',
                        'dispatcher': 'Welcome back, Dispatcher!',
                    }
                    
                    messages.success(request, role_messages.get(user.role, 'Welcome back!'))
                    
                    # Redirect based on role or next parameter
                    next_url = request.GET.get('next', 'dashboard')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Your account has been deactivated. Please contact your supervisor.')
            else:
                messages.error(request, 'Invalid badge number or password. Please try again.')
        else:
            messages.error(request, 'Please enter both badge number and password.')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    """
    Handle user logout
    """
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def dashboard_view(request):
    """
    Main dashboard with statistics and recent activities
    """
    # Get current date and time ranges
    now = timezone.now()
    today = now.date()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    
    # Basic Statistics
    stats = {
        'total_incidents': Incident.objects.count(),
        'open_incidents': Incident.objects.exclude(status__in=['resolved', 'closed']).count(),
        'recent_incidents': Incident.objects.filter(date_occurred__gte=last_7_days).count(),
        'total_arrests': Arrest.objects.count(),
        'active_officers': User.objects.filter(is_active_duty=True, role__in=['officer', 'detective']).count(),
        'evidence_items': Evidence.objects.count(),
        'emergency_calls_today': EmergencyCall.objects.filter(time_received__date=today).count(),
        'vehicles_in_system': Vehicle.objects.count(),
        'stolen_vehicles': Vehicle.objects.filter(is_stolen=True).count(),
        'equipment_assigned': Equipment.objects.filter(status='assigned').count(),
    }
    
    # Recent Activities (last 10)
    recent_incidents = Incident.objects.select_related(
        'crime_type', 'reporting_officer', 'station'
    ).order_by('-date_occurred')[:10]
    
    recent_arrests = Arrest.objects.select_related(
        'person', 'arresting_officer', 'incident'
    ).order_by('-date_arrested')[:10]
    
    recent_emergency_calls = EmergencyCall.objects.select_related(
        'assigned_officer', 'received_by'
    ).order_by('-time_received')[:10]
    
    # Priority Incidents (High and Critical priority)
    priority_incidents = Incident.objects.filter(
        priority__gte=3, 
        status__in=['reported', 'investigating']
    ).select_related('crime_type', 'investigating_officer')[:5]
    
    # Chart Data for Incidents by Status
    incident_status_data = Incident.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Chart Data for Incidents by Priority
    incident_priority_data = Incident.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    # Chart Data for Crime Types (Top 10)
    crime_type_data = Incident.objects.values(
        'crime_type__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Weekly Incident Trend (Last 7 days)
    weekly_trend = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = Incident.objects.filter(date_occurred__date=date).count()
        weekly_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%a'),
            'count': count
        })
    weekly_trend.reverse()
    
    # Monthly Statistics
    monthly_stats = []
    for i in range(6):
        month_start = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end - timedelta(days=month_end.day)
        
        incidents_count = Incident.objects.filter(
            date_occurred__range=[month_start, month_end]
        ).count()
        
        arrests_count = Arrest.objects.filter(
            date_arrested__range=[month_start, month_end]
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%b %Y'),
            'incidents': incidents_count,
            'arrests': arrests_count
        })
    
    monthly_stats.reverse()
    
    # Role-specific data
    user_role_data = {}
    if request.user.role == 'dispatcher':
        user_role_data = {
            'pending_calls': EmergencyCall.objects.filter(
                status__in=['received', 'dispatched']
            ).count(),
            'calls_today': EmergencyCall.objects.filter(
                time_received__date=today
            ).count()
        }
    elif request.user.role in ['officer', 'detective']:
        user_role_data = {
            'my_incidents': Incident.objects.filter(
                Q(reporting_officer=request.user) | Q(investigating_officer=request.user)
            ).count(),
            'my_arrests': Arrest.objects.filter(arresting_officer=request.user).count(),
            'assigned_calls': EmergencyCall.objects.filter(
                assigned_officer=request.user,
                status__in=['dispatched', 'responded']
            ).count()
        }
    elif request.user.role == 'supervisor':
        user_role_data = {
            'department_incidents': Incident.objects.filter(
                station__department__head_officer=request.user
            ).count(),
            'pending_reports': Incident.objects.filter(
                status='investigating',
                station__department__head_officer=request.user
            ).count()
        }
    
    # Equipment Status Distribution
    equipment_status = Equipment.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    context = {
        'stats': stats,
        'recent_incidents': recent_incidents,
        'recent_arrests': recent_arrests,
        'recent_emergency_calls': recent_emergency_calls,
        'priority_incidents': priority_incidents,
        'incident_status_data': list(incident_status_data),
        'incident_priority_data': list(incident_priority_data),
        'crime_type_data': list(crime_type_data),
        'weekly_trend': weekly_trend,
        'monthly_stats': monthly_stats,
        'user_role_data': user_role_data,
        'equipment_status': list(equipment_status),
        'user': request.user,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def dashboard_api(request):
    """
    API endpoint for dashboard data (for AJAX updates)
    """
    data_type = request.GET.get('type', 'stats')
    
    if data_type == 'stats':
        now = timezone.now()
        today = now.date()
        
        stats = {
            'total_incidents': Incident.objects.count(),
            'open_incidents': Incident.objects.exclude(status__in=['resolved', 'closed']).count(),
            'emergency_calls_today': EmergencyCall.objects.filter(time_received__date=today).count(),
            'active_officers': User.objects.filter(is_active_duty=True).count(),
        }
        return JsonResponse(stats)
    
    elif data_type == 'recent_incidents':
        incidents = Incident.objects.select_related(
            'crime_type', 'reporting_officer'
        ).order_by('-date_occurred')[:5]
        
        data = [{
            'id': inc.id,
            'incident_number': inc.incident_number,
            'title': inc.title,
            'status': inc.get_status_display(),
            'priority': inc.get_priority_display(),
            'date_occurred': inc.date_occurred.strftime('%Y-%m-%d %H:%M'),
            'officer': f"{inc.reporting_officer.first_name} {inc.reporting_officer.last_name}"
        } for inc in incidents]
        
        return JsonResponse({'incidents': data})
    
    return JsonResponse({'error': 'Invalid data type'}, status=400)