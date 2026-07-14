from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Department, Customer, Task, ActivityLog, Notification


def home(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == User.ROLE_SUPER_ADMIN:
                return redirect('super_admin_dashboard')
            elif user.role == User.ROLE_DEPARTMENT_MANAGER:
                return redirect('manager_dashboard')
            elif user.role == User.ROLE_EMPLOYEE:
                return redirect('employee_dashboard')

            return redirect('home')
        else:
            return render(
                request,
                'home.html',
                {'error': 'نام کاربری یا رمز عبور اشتباه است'}
            )

    return render(request, 'home.html')


@login_required
def super_admin_dashboard(request):
    if request.user.role != User.ROLE_SUPER_ADMIN:
        return redirect('home')

    if request.method == "POST":
        action = request.POST.get('action')
        model_name = request.POST.get('model_name')

        # ===== Department =====
        if model_name == 'department':
            if action == 'add':
                Department.objects.create(
                    name=request.POST.get('name'),
                    manager_id=request.POST.get('manager') or None,
                    parent_id=request.POST.get('parent') or None,
                )
                messages.success(request, 'دپارتمان ساخته شد.')

            elif action == 'edit':
                dep = get_object_or_404(Department, pk=request.POST.get('id'))
                dep.name = request.POST.get('name')
                dep.manager_id = request.POST.get('manager') or None
                dep.parent_id = request.POST.get('parent') or None
                dep.save()
                messages.success(request, 'دپارتمان ویرایش شد.')

            elif action == 'delete':
                Department.objects.filter(pk=request.POST.get('id')).delete()
                messages.success(request, 'دپارتمان حذف شد.')

        # ===== User =====
        elif model_name == 'user':
            if action == 'add':
                User.objects.create_user(
                    username=request.POST.get('username'),
                    password=request.POST.get('password'),
                    email=request.POST.get('email') or '',
                    role=request.POST.get('role'),
                    department_id=request.POST.get('department') or None,
                )
                messages.success(request, 'کاربر ساخته شد.')

            elif action == 'edit':
                # دسترسی کامل به سوپر ادمین برای ویرایش تمام فیلدهای کاربر که قبلاً نبود
                u = get_object_or_404(User, pk=request.POST.get('id'))
                u.username = request.POST.get('username')
                u.email = request.POST.get('email') or ''
                u.role = request.POST.get('role')
                u.department_id = request.POST.get('department') or None
                u.is_active = request.POST.get('is_active') == 'true'

                # امکان تغییر رمز عبور توسط سوپر ادمین
                new_password = request.POST.get('password')
                if new_password:
                    u.set_password(new_password)
                u.save()
                messages.success(request, 'اطلاعات کامل کاربر ویرایش شد.')

            elif action == 'delete':
                User.objects.filter(pk=request.POST.get('id')).delete()
                messages.success(request, 'کاربر حذف شد.')

        # ===== Customer =====
        elif model_name == 'customer':
            if action == 'add':
                Customer.objects.create(
                    first_name=request.POST.get('first_name'),
                    last_name=request.POST.get('last_name'),
                    phone_number=request.POST.get('phone_number'),
                    email=request.POST.get('email') or None,
                    passport_number=request.POST.get('passport_number') or None,
                    address=request.POST.get('address') or None,
                    description=request.POST.get('description') or None,
                    created_by=request.user,
                    status=request.POST.get('status'),
                )
                messages.success(request, 'مشتری ساخته شد.')

            elif action == 'edit':
                # سوپر ادمین می‌تواند همه چیز مشتری، حتی ثبت‌کننده را ویرایش کند
                c = get_object_or_404(Customer, pk=request.POST.get('id'))
                c.first_name = request.POST.get('first_name')
                c.last_name = request.POST.get('last_name')
                c.phone_number = request.POST.get('phone_number')
                c.email = request.POST.get('email') or None
                c.passport_number = request.POST.get('passport_number') or None
                c.address = request.POST.get('address') or None
                c.description = request.POST.get('description') or None
                c.status = request.POST.get('status')
                if request.POST.get('created_by'):
                    c.created_by_id = request.POST.get('created_by')
                c.save()
                messages.success(request, 'مشتری با تمام مشخصات ویرایش شد.')

            elif action == 'delete':
                Customer.objects.filter(pk=request.POST.get('id')).delete()
                messages.success(request, 'مشتری حذف شد.')

        # ===== Task =====
        elif model_name == 'task':
            if action == 'add':
                Task.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    customer_id=request.POST.get('customer'),  # فیلد اجباری جدید
                    assigned_to_id=request.POST.get('assigned_to'),
                    created_by=request.user,
                    stage=request.POST.get('stage'),
                    deadline=request.POST.get('deadline') or None,
                )
                messages.success(request, 'تسک ساخته شد.')

            elif action == 'edit':
                # سوپر ادمین کنترل کامل بر ویرایش تمام بخش‌های تسک دارد
                t = get_object_or_404(Task, pk=request.POST.get('id'))
                t.title = request.POST.get('title')
                t.description = request.POST.get('description')
                t.customer_id = request.POST.get('customer')  # امکان تغییر مشتری متصل به تسک
                t.assigned_to_id = request.POST.get('assigned_to')
                t.stage = request.POST.get('stage')
                t.deadline = request.POST.get('deadline') or None
                if request.POST.get('created_by'):
                    t.created_by_id = request.POST.get('created_by')
                t.save()
                messages.success(request, 'تسک با موفقیت ویرایش شد.')

            elif action == 'delete':
                Task.objects.filter(pk=request.POST.get('id')).delete()
                messages.success(request, 'تسک حذف شد.')

        return redirect('super_admin_dashboard')

    context = {
        'departments': Department.objects.select_related('manager', 'parent').all(),
        'users': User.objects.select_related('department').all(),
        # واکشی تسک‌ها به همراه سازنده و ارجاع شونده جهت نمایش در بخش مشتریان پنل
        'customers': Customer.objects.select_related('created_by').prefetch_related('tasks__assigned_to',
                                                                                    'tasks__created_by').all(),
        'tasks': Task.objects.select_related('customer', 'assigned_to', 'created_by').all(),
        'activity_logs': ActivityLog.objects.select_related('user', 'related_customer', 'related_task')[:50],
        'notifications': Notification.objects.select_related('recipient', 'sender', 'related_task')[:50],
    }
    return render(request, 'super_admin.html', context)


@login_required
def manager_dashboard(request):
    if request.user.role != User.ROLE_DEPARTMENT_MANAGER:
        return redirect('home')

    my_department = request.user.department
    if my_department:
        dept_users = User.objects.filter(department=my_department)
    else:
        dept_users = User.objects.filter(id=request.user.id)

    if request.method == "POST":
        action = request.POST.get('action')
        model_name = request.POST.get('model_name')

        # ===== Task =====
        if model_name == 'task':
            if action == 'add':
                assigned_user_id = request.POST.get('assigned_to')
                assigned_user = get_object_or_404(dept_users, id=assigned_user_id)

                Task.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    customer_id=request.POST.get('customer'),  # اتصال اجباری به مشتری
                    assigned_to=assigned_user,
                    created_by=request.user,
                    stage=request.POST.get('stage', 'created'),
                    deadline=request.POST.get('deadline') or None,
                )
                messages.success(request, 'تسک جدید برای دپارتمان ایجاد شد.')

            elif action == 'edit_stage':
                task_id = request.POST.get('id')
                new_stage = request.POST.get('stage')
                task = get_object_or_404(Task, pk=task_id, assigned_to__in=dept_users)
                task.stage = new_stage
                task.save()
                messages.success(request, 'وضعیت تسک به‌روزرسانی شد.')

        # ===== Customer =====
        elif model_name == 'customer':
            if action == 'add':
                Customer.objects.create(
                    first_name=request.POST.get('first_name'),
                    last_name=request.POST.get('last_name'),
                    phone_number=request.POST.get('phone_number'),
                    email=request.POST.get('email') or None,
                    passport_number=request.POST.get('passport_number') or None,
                    address=request.POST.get('address') or None,
                    description=request.POST.get('description') or None,
                    created_by=request.user,
                    status=request.POST.get('status'),
                )
                messages.success(request, 'مشتری جدید اضافه شد.')

            elif action == 'edit':
                # دسترسی ویرایش مشتری و تغییر وضعیت برای مدیر (متناسب با درخواست هر کسی بتواند ویرایش کند)
                c = get_object_or_404(Customer, pk=request.POST.get('id'))
                c.first_name = request.POST.get('first_name')
                c.last_name = request.POST.get('last_name')
                c.phone_number = request.POST.get('phone_number')
                c.email = request.POST.get('email') or None
                c.passport_number = request.POST.get('passport_number') or None
                c.address = request.POST.get('address') or None
                c.description = request.POST.get('description') or None
                c.status = request.POST.get('status')
                c.save()
                messages.success(request, 'مشخصات و وضعیت مشتری به‌روزرسانی شد.')

        return redirect('manager_dashboard')

    # واکشی تمام مشتریان سیستم به همراه تسک‌های متصل به آن‌ها برای نمایش جامع به مدیر
    all_customers = Customer.objects.select_related('created_by').prefetch_related('tasks__assigned_to',
                                                                                   'tasks__created_by').order_by(
        '-created_at')
    dept_tasks = Task.objects.filter(assigned_to__in=dept_users).select_related('customer', 'assigned_to',
                                                                                'created_by').order_by('-id')
    my_notifications = Notification.objects.filter(recipient=request.user).select_related('sender', 'related_task')

    context = {
        'department': my_department,
        'dept_users': dept_users,
        'tasks': dept_tasks,
        'customers': all_customers,
        'notifications': my_notifications,
        'open_tasks': dept_tasks.exclude(stage='completed'),
    }
    return render(request, 'manager.html', context)


@login_required
def employee_dashboard(request):
    if request.user.role != User.ROLE_EMPLOYEE:
        return redirect('home')

    if request.method == "POST":
        action = request.POST.get('action')
        model_name = request.POST.get('model_name')

        # ===== Task =====
        if model_name == 'task':
            if action == 'edit_stage':
                task_id = request.POST.get('id')
                new_stage = request.POST.get('stage')
                task = get_object_or_404(Task, pk=task_id, assigned_to=request.user)
                task.stage = new_stage
                task.save()
                messages.success(request, 'مرحله تسک با موفقیت تغییر کرد.')

        # ===== Customer =====
        elif model_name == 'customer':
            if action == 'add':
                Customer.objects.create(
                    first_name=request.POST.get('first_name'),
                    last_name=request.POST.get('last_name'),
                    phone_number=request.POST.get('phone_number'),
                    email=request.POST.get('email') or None,
                    passport_number=request.POST.get('passport_number') or None,
                    address=request.POST.get('address') or None,
                    description=request.POST.get('description') or None,
                    created_by=request.user,
                    status=request.POST.get('status'),
                )
                messages.success(request, 'مشتری جدید اضافه شد.')

            elif action == 'edit':
                # قابلیت ویرایش اطلاعات و تغییر Status مشتری توسط کارمندان عادی سیستم
                c = get_object_or_404(Customer, pk=request.POST.get('id'))
                c.first_name = request.POST.get('first_name')
                c.last_name = request.POST.get('last_name')
                c.phone_number = request.POST.get('phone_number')
                c.email = request.POST.get('email') or None
                c.passport_number = request.POST.get('passport_number') or None
                c.address = request.POST.get('address') or None
                c.description = request.POST.get('description') or None
                c.status = request.POST.get('status')
                c.save()
                messages.success(request, 'اطلاعات و وضعیت مشتری با موفقیت ویرایش شد.')

        return redirect('employee_dashboard')

    # کارمند تمام مشتریان را می‌بیند تا بتواند وضعیت هرکدام را بنا به نیاز تغییر دهد
    all_customers = Customer.objects.select_related('created_by').prefetch_related('tasks__assigned_to',
                                                                                   'tasks__created_by').order_by(
        '-created_at')
    my_tasks = Task.objects.filter(assigned_to=request.user).select_related('customer', 'created_by').order_by('-id')
    my_notifications = Notification.objects.filter(recipient=request.user).select_related('sender', 'related_task')

    context = {
        'tasks': my_tasks,
        'customers': all_customers,
        'notifications': my_notifications,
        'open_tasks': my_tasks.exclude(stage='completed'),
    }
    return render(request, 'employee.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')