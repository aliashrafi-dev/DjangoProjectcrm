from django.db import models
from django.contrib.auth.models import AbstractUser  # اینپورت درست برای توسعه کاربر پیش‌فرض
from django.conf import settings  # برای ارجاع استاندارد به مدل کاربر در بقیه مدل‌ها

class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('department_manager', 'Department Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # ارجاع به دپارتمان با استفاده از رشته 'Department' انجام شده چون این مدل در خطوط پایین‌تر تعریف شده است
    department = models.ForeignKey('Department', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Department(models.Model):
    name = models.CharField(max_length=100)
    # استفاده از settings.AUTH_USER_MODEL استانداردترین روش جنگو برای ارتباط با کاربر سفارشی است
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='managed_department', on_delete=models.SET_NULL, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('contract_signed', 'Contract Signed'),
        ('lost', 'Lost'),
    ])
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tasks', on_delete=models.CASCADE)
    stage = models.CharField(max_length=20, choices=[
        ('created', 'Created'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('completed', 'Completed'),
    ])
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    related_customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    related_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"