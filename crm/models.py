from django.db import models
from django.contrib.auth.models import AbstractUser  # اینپورت درست برای توسعه کاربر پیش‌فرض
from django.conf import settings  # برای ارجاع استاندارد به مدل کاربر در بقیه مدل‌ها
from django.core.exceptions import ValidationError


class User(AbstractUser):
    ROLE_SUPER_ADMIN = 'super_admin'
    ROLE_DEPARTMENT_MANAGER = 'department_manager'
    ROLE_EMPLOYEE = 'employee'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Admin'),
        (ROLE_DEPARTMENT_MANAGER, 'Department Manager'),
        (ROLE_EMPLOYEE, 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_EMPLOYEE)
    # ارجاع به دپارتمان با استفاده از رشته 'Department' انجام شده چون این مدل در خطوط پایین‌تر تعریف شده است
    # این فیلد یعنی «کاربر عضو کدوم دپارتمانه» (هم برای employee و هم برای manager)
    department = models.ForeignKey(
        'Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='members',
    )

    class Meta:
        ordering = ['username']
        indexes = [
            models.Index(fields=['role']),
        ]

    def clean(self):
        super().clean()
        # super_admin نباید عضو هیچ دپارتمانی باشه (چون روی کل سیستم دسترسی داره)
        if self.role == self.ROLE_SUPER_ADMIN and self.department_id:
            raise ValidationError({'department': 'کاربر Super Admin نباید به دپارتمانی متصل باشد.'})

        # اگر کاربر manager یک دپارتمانه، باید department خودش هم همون دپارتمان باشه
        managed = getattr(self, 'managed_department', None)
        if managed is not None and self.department_id != managed.id:
            raise ValidationError({
                'department': 'دپارتمان کاربر باید با دپارتمانی که مدیریت می‌کند یکسان باشد.'
            })

        # کسی که role اش department_manager هست باید حتماً به یک دپارتمان متصل باشه
        if self.role == self.ROLE_DEPARTMENT_MANAGER and not self.department_id and managed is None:
            raise ValidationError({'role': 'مدیر دپارتمان باید به یک دپارتمان متصل باشد.'})

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Department(models.Model):
    name = models.CharField(max_length=100)
    # هر منیجر فقط یک دپارتمان را مدیریت می‌کند => OneToOneField به‌جای ForeignKey
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='managed_department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'department_manager'},
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='sub_departments',
    )

    class Meta:
        ordering = ['name']

    def clean(self):
        super().clean()
        # جلوگیری از حلقه در سلسله‌مراتب (parent نباید خودش یا یکی از فرزندانش باشه)
        if self.parent_id:
            node = self.parent
            visited = set()
            while node is not None:
                if node.pk == self.pk or node.pk in visited:
                    raise ValidationError({'parent': 'ایجاد حلقه در سلسله‌مراتب دپارتمان مجاز نیست.'})
                visited.add(node.pk)
                node = node.parent

        # منیجر انتخاب‌شده باید نقش department_manager داشته باشد
        if self.manager_id and self.manager.role != 'department_manager':
            raise ValidationError({'manager': 'کاربر انتخاب‌شده باید نقش «مدیر دپارتمان» داشته باشد.'})

    def __str__(self):
        return self.name


class Customer(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_CONTRACT_SIGNED = 'contract_signed'
    STATUS_LOST = 'lost'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_CONTRACT_SIGNED, 'Contract Signed'),
        (STATUS_LOST, 'Lost'),
    ]

    name = models.CharField(max_length=100)
    contact_info = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_NEW)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name


class Task(models.Model):
    STAGE_CREATED = 'created'
    STAGE_IN_PROGRESS = 'in_progress'
    STAGE_REVIEW = 'review'
    STAGE_COMPLETED = 'completed'

    STAGE_CHOICES = [
        (STAGE_CREATED, 'Created'),
        (STAGE_IN_PROGRESS, 'In Progress'),
        (STAGE_REVIEW, 'Review'),
        (STAGE_COMPLETED, 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tasks', on_delete=models.CASCADE)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default=STAGE_CREATED)
    deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['stage']),
        ]

    def clean(self):
        super().clean()
        # کارمند اختصاص‌یافته باید عضو همون دپارتمانی باشه که ایجادکننده (منیجر) بهش تعلق داره
        # (در صورتی که هر دو department مشخص داشته باشن)
        if (
            self.assigned_to_id
            and self.created_by_id
            and self.created_by.department_id
            and self.assigned_to.department_id
            and self.created_by.department_id != self.assigned_to.department_id
            and self.created_by.role != User.ROLE_SUPER_ADMIN
        ):
            raise ValidationError({
                'assigned_to': 'تسک فقط می‌تواند به کارمندِ همان دپارتمان اختصاص داده شود.'
            })

    def __str__(self):
        return self.title


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    related_customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    related_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"


class Notification(models.Model):
    TYPE_TASK_ASSIGNED = 'task_assigned'
    TYPE_TASK_STAGE_CHANGED = 'task_stage_changed'
    TYPE_TASK_DEADLINE_SOON = 'task_deadline_soon'

    TYPE_CHOICES = [
        (TYPE_TASK_ASSIGNED, 'Task Assigned'),
        (TYPE_TASK_STAGE_CHANGED, 'Task Stage Changed'),
        (TYPE_TASK_DEADLINE_SOON, 'Task Deadline Soon'),
    ]

    # کسی که نوتیفیکیشن رو دریافت می‌کنه (کارمندی که تسک بهش assign شده)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE,
    )
    # کسی که باعث ایجاد نوتیفیکیشن شده (مدیر/ادمینی که تسک رو فرستاده)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_notifications',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_TASK_ASSIGNED)
    message = models.CharField(max_length=255)
    related_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.recipient.username} - {self.message}"