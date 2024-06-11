from django.urls import path, include
from todo_list_app import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

router.register(r'categories', views.CategoryViewSet, basename='category')

app_name = 'todo_list'
urlpatterns = [
    path('', include(router.urls)),
    path('tasks', views.tasks, name='tasks'),
    path('tasks/create', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/delete', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/update', views.task_update, name='task_update'),
]