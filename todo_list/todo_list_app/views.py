from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Category, Task
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django import forms


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('todo_list:index')
        else:
            messages.success(request, 'There was an error logging in.')
            return redirect('todo_list:login')
    else:
        form = LoginForm()
        return render(request, 'auth/login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('todo_list:index')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


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
            return redirect('todo_list:index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth/register.html', {'form': form})


def index(request):
    return render(request, 'todo_list_app/index.html')


@login_required
def all_categories(request):

    query = request.GET.get('q')
    category_list = Category.objects.filter(user=request.user)
    if query:
        category_list = category_list.filter(name__icontains=query)
    return render(request, 'todo_list_app/all_categories.html', {'category_list': category_list,'query':query})


@login_required
def delete_category(request, category_id):
    Category.objects.get(id=category_id, user=request.user).delete()
    return redirect('todo_list:all_categories')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


@login_required
def update_category(request, category_id):
    category = Category.objects.get(id=category_id, user=request.user)
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


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'completed','category']


@login_required
def tasks(request):
    query = request.GET.get('q')
    task_list = Task.objects.filter(category__user=request.user)
    if query:
        task_list = task_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query))
    return render(request, 'todo_list_app/tasks.html', {
        'task_list': task_list,
        'query': query
    })


@login_required
def task_delete(request, task_id):
    Task.objects.get(id=task_id, category__user=request.user).delete()
    return redirect('todo_list:tasks')


@login_required
def task_create(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo_list:tasks')
    else:
        form = TaskForm()
        return render(request, 'todo_list_app/task_create.html', {'form': form,'categories': categories})


@login_required
def task_update(request, task_id):
    task = Task.objects.get(id=task_id)
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST,instance=task)
        if form.is_valid():
            form.save()
        return redirect('todo_list:tasks')
    else:
        form = TaskForm()
        return render(request,
                      'todo_list_app/task_update.html',
                      {'task':
                          task, 'categories': categories,'form': form})
