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
    # فیلدهایی که در جدول لیست کاربران نشان داده می‌شوند
    list_display = (
        'username',
        'email',
        'role',
        'department',
        'is_active',
    )

    # فیلترهای سمت راست جدول
    list_filter = (
        'role',
        'department',
        'is_active',
    )

    # فیلدهای قابل جستجو
    search_fields = (
        'username',
        'email',
    )

    # اضافه کردن فیلدهای سفارشی شما به فرم ویرایش کاربر
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات نقش و دسترسی', {'fields': ('role', 'department')}),
    )

    # اضافه کردن فیلدهای سفارشی شما به فرم ساخت کاربر جدید
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


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'status',
        'created_by',
    )
    list_filter = (
        'status',
    )
    search_fields = (
        'name',
        'contact_info',
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
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