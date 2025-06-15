
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.login_view , name='login'),
    path('logout/', views.logout_view , name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
