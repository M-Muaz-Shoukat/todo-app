from django.urls import path
from . import views
app_name = 'todo_list'
urlpatterns = [
    path('categories/', views.index, name='all_categories'),
    path('category/create', views.create_category, name='create_category'),
    path('category/<int:category_id>/update', views.update_category, name='category_update'),
    path('category/<int:category_id>/delete', views.delete_category, name='category_delete'),
    path('category/<int:category_id>/tasks', views.category_tasks, name='category_tasks'),
    path('category/<int:category_id>/tasks/create', views.category_task_create, name='category_task_create'),
    path('category/<int:category_id>/tasks/<int:task_id>/delete', views.category_task_delete, name='category_task_delete'),
    path('category/<int:category_id>/tasks/<int:task_id>/update', views.category_task_update, name='category_task_update'),
]
