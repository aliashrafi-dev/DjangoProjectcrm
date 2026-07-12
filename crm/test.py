from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
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
            return render(request, 'home.html', {'error': 'نام کاربری یا رمز عبور اشتباه است'})

    return render(request, 'home.html')


@login_required
def super_admin_dashboard(request):
    # فقط super_admin اجازه دسترسی داره
    if request.user.role != User.ROLE_SUPER_ADMIN:
        return redirect('home')

    # ---------- مدیریت POST ها (ساخت / ویرایش / حذف) ----------
    if request.method == "POST":
        action = request.POST.get('action')   # مثلا: add_department, edit_department, delete_department, ...
        model_name = request.POST.get('model_name')  # department, customer, task, user, ...

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
                u = User.objects.create_user(
                    username=request.POST.get('username'),
                    password=request.POST.get('password'),
                    role=request.POST.get('role'),
                    department_id=request.POST.get('department') or None,
                )
                messages.success(request, 'کاربر ساخته شد.')

            elif action == 'edit':
                u = get_object_or_404(User, pk=request.POST.get('id'))
                u.username = request.POST.get('username')
                u.role = request.POST.get('role')
                u.department_id = request.POST.get('department') or None
                u.save()
                messages.success(request, 'کاربر ویرایش شد.')

            elif action == 'delete':
                User.objects.filter(pk=request.POST.get('id')).delete()
                messages.success(request, 'کاربر حذف شد.')

        # ===== Customer =====
        elif model_name == 'customer':
            if action == 'add':
                Customer.objects.create(
                    name=request.POST.get('name'),
                    contact_info=request.POST.get('contact_info'),
                    created_by=request.user,
                    status=request.POST.get('status'),
                    description=request.POST.get('description'),
                )
                messages.success(request, 'مشتری ساخته شد.')

            elif action == 'edit':
                c = get_object_or_404(Customer, pk=request.POST.get('id'))
                c.name = request.POST.get('name')
                c.contact_info = request.POST.get('contact_info')
                c.status = request.POST.get('status')
                c.description = request.POST.get('description')
                c.save()
                messages.success(request, 'مشتری ویرایش شد.')

            elif action == 'delete':
                Customer.objects.filter(pk=request.POST.get('id')).delete()
                messages.success(request, 'مشتری حذف شد.')

        # ===== Task =====
        elif model_name == 'task':
            if action == 'add':
                Task.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    assigned_to_id=request.POST.get('assigned_to'),
                    created_by=request.user,
                    stage=request.POST.get('stage'),
                    deadline=request.POST.get('deadline') or None,
                )
                messages.success(request, 'تسک ساخته شد.')

            elif action == 'edit':
                t = get_object_or_404(Task, pk=request.POST.get('id'))
                t.title = request.POST.get('title')
                t.description = request.POST.get('description')
                t.assigned_to_id = request.POST.get('assigned_to')
                t.stage = request.POST.get('stage')
                t.deadline = request.POST.get('deadline') or None
                t.save()
                messages.success(request, 'تسک ویرایش شد.')

            elif action == 'delete':
                Task.objects.filter(pk=request.POST.get('id')).delete()
                messages.success(request, 'تسک حذف شد.')

        return redirect('super_admin_dashboard')

    # ---------- گرفتن داده‌ها برای نمایش (GET) ----------
    context = {
        'departments': Department.objects.select_related('manager', 'parent').all(),
        'users': User.objects.select_related('department').all(),
        'customers': Customer.objects.select_related('created_by').all(),
        'tasks': Task.objects.select_related('assigned_to', 'created_by').all(),
        'activity_logs': ActivityLog.objects.select_related('user', 'related_customer', 'related_task')[:50],
        'notifications': Notification.objects.select_related('recipient', 'sender', 'related_task')[:50],
    }
    return render(request, 'super_admin.html', context)


@login_required
def manager_dashboard(request):
    return render(request, 'manager.html')


@login_required
def employee_dashboard(request):
    return render(request, 'employee.html')


def logout_user(request):
    return redirect('home')