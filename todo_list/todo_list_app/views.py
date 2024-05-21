from django.shortcuts import render, redirect
from .models import Category, Task
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django import forms


def login_user(request):
    return render(request, 'auth/login.html', {})


def index(request):
    return render(request, 'todo_list_app/index.html')


def all_categories(request):
    query = request.GET.get('q')
    category_list = Category.objects.all()

    if query:
        category_list = category_list.filter(name__icontains=query)
    return render(request, 'todo_list_app/all_categories.html', {'category_list': category_list,'query':query})


def delete_category(request, category_id):
    Category.objects.get(id=category_id).delete()
    return redirect('todo_list:all_categories')


def update_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        category.name = name
        category.save()
        return redirect('todo_list:all_categories')
    else:
        return render(request, 'todo_list_app/category_update.html', {'category': category})


def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user_id = 1
            category.save()
            return redirect('todo_list:all_categories')
    else:
        form = CategoryForm()
    return render(request, 'todo_list_app/category_create.html', {'form': form})


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'completed','category']


def tasks(request):
    query = request.GET.get('q')
    task_list = Task.objects.all()
    if query:
        task_list = task_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query))
    return render(request, 'todo_list_app/tasks.html', {
        'task_list': task_list,
        'query': query
    })


def task_delete(request, task_id):
    Task.objects.get(id=task_id).delete()
    return redirect('todo_list:tasks')


def task_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo_list:tasks')
    else:
        form = TaskForm()
        return render(request, 'todo_list_app/task_create.html', {'form': form,'categories': categories})


def task_update(request, task_id):
    task = Task.objects.get(id=task_id)
    categories = Category.objects.all()
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
