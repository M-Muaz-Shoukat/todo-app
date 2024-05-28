import pytz
from datetime import datetime
from todo_list_app.models import Task


def local_to_utc(user_timezone, reminder):

    if user_timezone:
        user_tz = pytz.timezone(user_timezone)
    else:
        user_tz = pytz.utc
    remind_at = datetime.strptime(reminder.remind_at, '%Y-%m-%dT%H:%M')
    localized_remind_at = user_tz.localize(remind_at, is_dst=None)
    reminder.remind_at = localized_remind_at.astimezone(pytz.utc)


def reminder_create_or_update(user, reminder, timezone, task_id):
    local_to_utc(timezone, reminder)
    reminder.user = user
    reminder.task = Task.objects.get(id=task_id)
    return reminder.save()


