from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    Department,
    Customer,
    Task,
    ActivityLog,
    Notification,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'department',
        'is_active',
    )
    list_filter = (
        'role',
        'department',
        'is_active',
    )
    search_fields = (
        'username',
        'email',
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات نقش و دسترسی', {'fields': ('role', 'department')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('اطلاعات نقش و دسترسی', {'fields': ('role', 'department')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'manager',
        'parent',
    )
    search_fields = (
        'name',
    )


# این کلاس باعث می‌شود تسک‌های هر مشتری درون صفحه خود مشتری نمایش داده شوند
class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('title', 'created_by', 'assigned_to', 'stage', 'deadline')
    readonly_fields = ('created_by',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'unique_code',
        'first_name',
        'last_name',
        'phone_number',
        'status',
        'created_by',
        'created_at',
    )
    list_filter = (
        'status',
        'created_at',
    )
    search_fields = (
        'unique_code',
        'first_name',
        'last_name',
        'phone_number',
        'email',
    )
    readonly_fields = ('unique_code', 'created_at')
    inlines = [TaskInline]  # اتصال تسک‌ها به نمایش مشتری


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'customer',
        'assigned_to',
        'created_by',
        'stage',
        'deadline',
    )
    list_filter = (
        'stage',
    )
    search_fields = (
        'title',
        'description',
        'customer__first_name',
        'customer__last_name',
        'customer__unique_code',
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'action',
        'timestamp',
    )
    list_filter = (
        'timestamp',
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient',
        'sender',
        'notification_type',
        'is_read',
        'created_at',
    )
    list_filter = (
        'notification_type',
        'is_read',
    )