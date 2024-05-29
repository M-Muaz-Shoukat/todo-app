from django.urls import path
from . import views
app_name = 'todo_list'
urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.all_categories, name='all_categories'),
    path('category/create', views.create_category, name='create_category'),
    path('category/<int:category_id>/update', views.update_category, name='category_update'),
    path('category/<int:category_id>/delete', views.delete_category, name='category_delete'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/delete', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/update', views.task_update, name='task_update'),
    path('auth/login', views.login_user, name='login'),
    path('auth/logout', views.logout_user, name='logout'),
    path('auth/register', views.register_user, name='register'),
]
