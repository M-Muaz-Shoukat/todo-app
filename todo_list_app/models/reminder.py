from django.db import models
from django.contrib.auth.models import User
from todo_list_app.models.tasks import Task


class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    remind_at = models.DateTimeField()
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} {self.task} {self.remind_at}'

