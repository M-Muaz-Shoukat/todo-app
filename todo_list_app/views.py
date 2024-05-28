from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from todo_list_app.models import Category, Task, Reminder
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, CustomUserCreationForm, TaskForm, CategoryForm
from todo_list_app.utility import reminder_create_or_update


class LoginError(Exception):
    pass


def login_user(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is None:
                raise LoginError('Invalid username or password')
            login(request, user)
            return redirect('index')
        except LoginError as e:
            messages.error(request, str(e))
            return redirect('login')
    else:
        form = LoginForm()
        return render(request, 'auth/login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'You have been registered successfully.')
            return redirect('index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth/register.html', {'form': form})


def index(request):
    return render(request, 'todo_list_app/index.html')


@login_required
def all_categories(request):
    query = request.GET.get('q')
    category_list = Category.objects.filter(user=request.user, name__icontains=query if query else '')
    return render(request, 'todo_list_app/all_categories.html', {'category_list': category_list, 'query': query})


@login_required
def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id, user=request.user)
        if category is None:
            raise ObjectDoesNotExist
        category.delete()
        return redirect('todo_list:all_categories')
    except ObjectDoesNotExist:
        messages.error(request, 'Category does not exist')
        return redirect('todo_list:all_categories')


@login_required
def update_category(request, category_id):
    try:
        category = get_object_or_404(Category, id=category_id, user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Category does not exist')
        return redirect('todo_list:all_categories')
    if request.method == 'POST':
        name = request.POST.get('name')
        category.name = name
        category.save()
        return redirect('todo_list:all_categories')
    else:
        return render(request, 'todo_list_app/category_update.html', {'category': category})


@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user_id = request.user.id
            category.save()
            return redirect('todo_list:all_categories')
    else:
        form = CategoryForm()
        return render(request, 'todo_list_app/category_create.html', {'form': form})


@login_required
def tasks(request):
    query = request.GET.get('q')
    try:
        task_list = Task.objects.filter(category__user=request.user)

        if query:
            task_list = task_list.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )

        tasks_with_reminders = []
        for task in task_list:
            try:
                task_reminders = Reminder.objects.filter(task=task)
                tasks_with_reminders.append({
                    'task': task,
                    'reminder': task_reminders[0] if task_reminders else None
                })
            except Reminder.DoesNotExist:
                messages.error(request, f"Reminder for task {task.id} does not exist.")

        return render(request, 'todo_list_app/tasks.html', {
            'tasks_with_reminders': tasks_with_reminders,
            'query': query
        })

    except Task.DoesNotExist:
        messages.error(request, "No tasks found for the current user.")
        return render(request, 'todo_list_app/tasks.html', {
            'tasks_with_reminders': [],
            'query': query
        })


@login_required
def task_delete(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id, category__user=request.user)
        task.delete()
        return redirect('todo_list:tasks')
    except ObjectDoesNotExist:
        messages.error(request, 'No such task')
        return redirect('todo_list:tasks')


@login_required
def task_create(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            remind_at = request.POST.get('remind_at')
            timezone = request.POST.get('timezone')
            task = form.save()
            if remind_at != '':
                reminder = Reminder(remind_at=remind_at)
                reminder_create_or_update(request.user, reminder, timezone, task.id)
            return redirect('todo_list:tasks')
    else:
        form = TaskForm()
        return render(request, 'todo_list_app/task_create.html', {'form': form, 'categories': categories})


@login_required
def task_update(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
    except ObjectDoesNotExist:
        messages.error(request, 'No such task')
        return redirect('todo_list:tasks')
    try:
        reminder = Reminder.objects.get(task=task)
    except Reminder.DoesNotExist:
        reminder = None

    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            remind_at = request.POST.get('remind_at')
            timezone = request.POST.get('timezone')
            task = form.save()
            if remind_at != '':
                if reminder is None:
                    reminder = Reminder(remind_at=remind_at)
                else:
                    reminder.remind_at = remind_at
                reminder_create_or_update(request.user, reminder, timezone, task.id)

        return redirect('todo_list:tasks')
    else:
        form = TaskForm()
        return render(request,
                      'todo_list_app/task_update.html',
                      {'task':
                           task, 'categories': categories, 'reminder': reminder, 'form': form})
