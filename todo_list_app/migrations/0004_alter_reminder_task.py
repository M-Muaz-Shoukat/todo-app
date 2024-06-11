# Generated by Django 5.0.6 on 2024-06-10 13:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_list_app', '0003_alter_reminder_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reminder',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminder', to='todo_list_app.task'),
        ),
    ]
