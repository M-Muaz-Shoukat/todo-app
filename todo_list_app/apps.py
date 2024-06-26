from django.apps import AppConfig


class TodoListAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'todo_list_app'

    def ready(self):
        import todo_list_app.signals

