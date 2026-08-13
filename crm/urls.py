from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/super-admin/', views.super_admin_dashboard,
         name='super_admin_dashboard'),
    path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/employee/', views.employee_dashboard,
         name='employee_dashboard'),
    path('logout/', views.logout_user, name='logout'),




]
