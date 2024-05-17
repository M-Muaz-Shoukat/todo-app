from django.shortcuts import render, redirect
from .models import Category, Task
from django import forms
# Create your views here.


def index(request):
    category_list = Category.objects.all()
    return render(request, 'todo_list_app/index.html', {'category_list': category_list})


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
        fields = ['title', 'description', 'due_date', 'completed']


def category_tasks(request, category_id):
    category = Category.objects.get(id=category_id)
    task_list = Task.objects.filter(category_id=category_id)
    return render(request, 'todo_list_app/category_tasks.html', {'task_list': task_list, 'category': category})


def category_task_delete(request,category_id, task_id):
    Task.objects.get(id=task_id).delete()
    return redirect('todo_list:category_tasks', category_id)


def category_task_create(request, category_id):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.category_id = category_id
            task.save()
            return redirect('todo_list:category_tasks',category_id=category_id)
    else:
        form = TaskForm()
        return render(request, 'todo_list_app/category_task_create.html', {'form': form})


def category_task_update(request, category_id, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.due_date = request.POST.get('due_date')
        task.completed = bool(request.POST.get('completed'))
        task.save()
        return redirect('todo_list:category_tasks', category_id=category_id)
    else:
        return render(request, 'todo_list_app/category_task_update.html', {'category_id': category_id, 'task': task})

