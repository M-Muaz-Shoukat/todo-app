from django.urls import resolve
from datetime import datetime
from todo_list_app.models import RequestLogs


class RequestCountAndAvgTime:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        view_name = resolve(request.path_info).view_name
        print(f"View name: {view_name}")

        start_time = datetime.now()

        response = self.get_response(request)

        end_time = datetime.now()
        elapsed_time = round((end_time - start_time).total_seconds() * 1000, 2)
        print(f"Elapsed time: {elapsed_time}")
        obj, created = RequestLogs.objects.get_or_create(name=view_name,
                                                         defaults={'avg_time': elapsed_time, 'count': 1})

        if not created:
            total_time = obj.avg_time * obj.count + elapsed_time
            obj.count += 1
            obj.avg_time = round(total_time / obj.count, 2)
            obj.save()
        print(f"Model avg time: {obj.avg_time}")
        print(f"Request Logs:\n\t Request Name: {obj.name} \n\t Avg Time:  {obj.avg_time}  \n\t Count:  {obj.count}")

        return response

