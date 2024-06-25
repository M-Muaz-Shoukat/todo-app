from django.db import models


class RequestLogs(models.Model):
    name = models.CharField(max_length=120)
    avg_time = models.FloatField()
    count = models.IntegerField()

    def __str__(self):
        return f'{self.name} {self.avg_time} {self.count}'

