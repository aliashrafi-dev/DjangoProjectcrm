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

            # بررسی دقیق مقدار فیلد role بر اساس مدل شما
            if user.role == User.ROLE_SUPER_ADMIN:
                return redirect('super_admin_dashboard')

            elif user.role == User.ROLE_DEPARTMENT_MANAGER:
                return redirect('manager_dashboard')

            elif user.role == User.ROLE_EMPLOYEE:
                return redirect('employee_dashboard')

            # حالت پیش‌فرض اگر نقش کاربر با هیچ‌کدام سازگار نبود
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
    # جلوگیری از دسترسی نقش‌های دیگر[cite: 3]
    if request.user.role != User.ROLE_DEPARTMENT_MANAGER:
        return redirect('home')

    # پیدا کردن دپارتمان کاربر فعلی و اعضای آن
    my_department = request.user.department
    if my_department:
        # واکشی تمام کاربرانی که در این دپارتمان هستند
        dept_users = User.objects.filter(department=my_department)
    else:
        # اگر مدیر دپارتمانی نداشت، فقط خودش را در نظر می‌گیریم
        dept_users = User.objects.filter(id=request.user.id)

    # ---------- مدیریت POST ها ----------
    if request.method == "POST":
        action = request.POST.get('action')
        model_name = request.POST.get('model_name')

        # ===== Task =====
        if model_name == 'task':
            if action == 'add':
                # مدیر می‌تواند تسک بسازد و به کارمندان دپارتمان خودش اختصاص دهد
                assigned_user_id = request.POST.get('assigned_to')
                assigned_user = get_object_or_404(dept_users, id=assigned_user_id)

                Task.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    assigned_to=assigned_user,
                    created_by=request.user,
                    stage=request.POST.get('stage', 'created'),
                    deadline=request.POST.get('deadline') or None,
                )
                messages.success(request, 'تسک جدید برای دپارتمان ایجاد شد.')

            elif action == 'edit_stage':
                task_id = request.POST.get('id')
                new_stage = request.POST.get('stage')
                # مدیر فقط می‌تواند تسک‌های دپارتمان خودش را تغییر وضعیت دهد
                task = get_object_or_404(Task, pk=task_id, assigned_to__in=dept_users)
                task.stage = new_stage
                task.save()
                messages.success(request, 'وضعیت تسک به‌روزرسانی شد.')

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
                messages.success(request, 'مشتری جدید اضافه شد.')

        return redirect('manager_dashboard')

    # ---------- گرفتن داده‌ها برای نمایش (GET) ----------
    # فیلتر تسک‌ها و مشتریانی که مربوط به کاربران این دپارتمان هستند
    dept_tasks = Task.objects.filter(assigned_to__in=dept_users).select_related('assigned_to', 'created_by').order_by(
        '-id')
    dept_customers = Customer.objects.filter(created_by__in=dept_users).select_related('created_by').order_by('-id')
    my_notifications = Notification.objects.filter(recipient=request.user).select_related('sender', 'related_task')

    context = {
        'department': my_department,
        'dept_users': dept_users,
        'tasks': dept_tasks,
        'customers': dept_customers,
        'notifications': my_notifications,
        'open_tasks': dept_tasks.exclude(stage='completed'),
    }
    return render(request, 'manager.html', context)




@login_required
def employee_dashboard(request):
    # جلوگیری از دسترسی سایر نقش‌ها به این پنل[cite: 3]
    if request.user.role != User.ROLE_EMPLOYEE:
        return redirect('home')

    # ---------- مدیریت POST ها (ویرایش مرحله تسک / افزودن مشتری) ----------
    if request.method == "POST":
        action = request.POST.get('action')
        model_name = request.POST.get('model_name')

        # ===== Task =====
        if model_name == 'task':
            if action == 'edit_stage':
                task_id = request.POST.get('id')
                new_stage = request.POST.get('stage')

                # بررسی اینکه تسک حتما به همین کارمند اختصاص داده شده باشد[cite: 3]
                task = get_object_or_404(Task, pk=task_id, assigned_to=request.user)
                task.stage = new_stage
                task.save()
                messages.success(request, 'مرحله تسک با موفقیت تغییر کرد.')

        # ===== Customer =====
        elif model_name == 'customer':
            if action == 'add':
                Customer.objects.create(
                    name=request.POST.get('name'),
                    contact_info=request.POST.get('contact_info'),
                    created_by=request.user,  # ثبت مشتری به نام همین کارمند[cite: 3]
                    status=request.POST.get('status'),
                    description=request.POST.get('description'),
                )
                messages.success(request, 'مشتری جدید اضافه شد.')

        return redirect('employee_dashboard')

    # ---------- گرفتن داده‌ها برای نمایش (GET) ----------
    # فیلتر کردن داده‌ها به طوری که کارمند فقط اطلاعات خودش را ببیند[cite: 3]
    my_tasks = Task.objects.filter(assigned_to=request.user).select_related('created_by').order_by('-id')
    my_customers = Customer.objects.filter(created_by=request.user).order_by('-id')

    # واکشی نوتیفیکیشن‌های مربوط به همین کارمند[cite: 3]
    my_notifications = Notification.objects.filter(recipient=request.user).select_related('sender', 'related_task')

    context = {
        'tasks': my_tasks,
        'customers': my_customers,
        'notifications': my_notifications,
        # فیلتر کردن تسک‌های باز (تکمیل نشده) برای نمایش در بخش نوتیفیکیشن‌ها یا آمار
        'open_tasks': my_tasks.exclude(stage='completed'),
    }
    return render(request, 'employee.html', context)

def logout_user(request):
    return redirect('home')






