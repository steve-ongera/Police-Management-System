# police/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Auth routes
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard routes
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/api/', views.dashboard_api, name='dashboard_api'),
]
