from django.urls import path, include
from todo_list_app import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'tasks', views.TaskViewSet, basename='task')

app_name = 'todo_list'
urlpatterns = [
    path('', include(router.urls))
]

