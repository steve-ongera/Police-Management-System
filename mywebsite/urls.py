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
    path('officers/', views.officer_list , name="officers"),
    path('officer/<int:officer_id>/', views.officer_detail_view, name='officer_detail'),

]
