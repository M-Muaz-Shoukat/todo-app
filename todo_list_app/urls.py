from django.urls import path
from todo_list_app import views
from todo_list_app.tasks import check_and_send_reminders

app_name = 'todo_list'
urlpatterns = [
    path('categories/', views.all_categories, name='all_categories'),
    path('category/create', views.create_category, name='create_category'),
    path('category/<int:category_id>/update', views.update_category, name='category_update'),
    path('category/<int:category_id>/delete', views.delete_category, name='category_delete'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/delete', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/update', views.task_update, name='task_update'),
    path('tasks/<int:task_id>/reminder/create', views.create_reminder, name='reminder_create'),
    path('tasks/reminder/<int:reminder_id>/update', views.update_reminder, name='reminder_update'),
]