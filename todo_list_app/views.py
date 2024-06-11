from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from todo_list_app.models import Category, Task, Reminder
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from todo_list_app.utils import reminder_create_or_update, send_code_to_user, verify_otp_code
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from todo_list_app.models import User
from rest_framework.generics import GenericAPIView
from todo_list_app.serializers import UserRegisterSerializer, UserLoginSerializer, LogoutSerializer, CategorySerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import permissions
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])
            send_code_to_user(user_data['email'], user.id)
            user_id = urlsafe_base64_encode(smart_bytes(user.id))
            return Response({'data': user_data, 'user_id': user_id, 'message': f"Account Registered Successfully!"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmailView(GenericAPIView):

    def post(self, request):
        otp_code = request.data.get('code')
        user_id = request.data.get('user_id')
        if not user_id or not isinstance(user_id, str):
            return Response({'message': 'Invalid user_id format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = int(force_str(urlsafe_base64_decode(user_id)))
            if not verify_otp_code(otp_code, user_id):
                return Response({
                    'message': 'Code is Invalid'
                }, status=status.HTTP_404_NOT_FOUND)
            user = User.objects.get(id=user_id)
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message': 'Account Email Verified Successfully!'
                }, status=status.HTTP_200_OK)

            return Response({
                'message': 'User Already Verified!'
            }, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'message': 'Code not Provided'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials try again!')
        user_token = user.tokens()
        if not user.is_verified:
            send_code_to_user(user.email, user.id)
            user_id = urlsafe_base64_encode(smart_bytes(user.id))
            return Response({
                'email': user.email,
                'full_name': user.get_full_name,
                'user_id': user_id,
                'message': 'Email is not verified! An email has been sent to your Email Address Verify it.'
            }, status=status.HTTP_208_ALREADY_REPORTED)
        return Response({
            'email': serializer.data['email'],
            'full_name': user.get_full_name,
            'access_token': str(user_token.get('access')),
            'refresh_token': str(user_token.get('refresh')),
        }, status=status.HTTP_200_OK)


class LogoutUserView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


def index(request):
    return render(request, 'todo_list_app/index.html')


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        return obj.user == request.user


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Category.objects.filter(name__icontains=query, user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@login_required
def tasks(request):
    query = request.GET.get('q')
    try:
        task_list = Task.objects.filter(category__user=request.user)

        if query:
            task_list = task_list.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )

        tasks_with_reminders = []
        for task in task_list:
            try:
                task_reminders = Reminder.objects.filter(task=task)
                tasks_with_reminders.append({
                    'task': task,
                    'reminder': task_reminders[0] if task_reminders else None
                })
            except Reminder.DoesNotExist:
                messages.error(request, f"Reminder does not exist for task {task.id}.")

        return render(request, 'todo_list_app/tasks.html', {
            'tasks_with_reminders': tasks_with_reminders,
            'query': query
        })

    except Task.DoesNotExist:
        messages.error(request, "No Tasks Found for the current User.")
        return render(request, 'todo_list_app/tasks.html', {
            'tasks_with_reminders': [],
            'query': query
        })


@login_required
def task_delete(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id, category__user=request.user)
        task.delete()
        return redirect('todo_list:tasks')
    except ObjectDoesNotExist:
        messages.error(request, 'No Task Found!')
        return redirect('todo_list:tasks')


@login_required
def task_create(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            remind_at = request.POST.get('remind_at')
            timezone = request.POST.get('timezone')
            task = form.save()
            if remind_at != '':
                reminder = Reminder(remind_at=remind_at)
                reminder_create_or_update(request.user, reminder, timezone, task.id)
            return redirect('todo_list:tasks')
        else:
            messages.error(request,'Please Fill all the Input Fields')
            return render(request, 'todo_list_app/task_create.html', {'form': form, 'categories': categories})
    else:
        form = TaskForm()
        return render(request, 'todo_list_app/task_create.html', {'form': form, 'categories': categories})


@login_required
def task_update(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
    except ObjectDoesNotExist:
        messages.error(request, 'No Task Found!')
        return redirect('todo_list:tasks')
    try:
        reminder = Reminder.objects.get(task=task)
    except Reminder.DoesNotExist:
        reminder = None

    categories = Category.objects.filter(user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            remind_at = request.POST.get('remind_at')
            timezone = request.POST.get('timezone')
            task = form.save()
            if remind_at != '':
                if reminder is None:
                    reminder = Reminder(remind_at=remind_at)
                else:
                    reminder.remind_at = remind_at
                reminder_create_or_update(request.user, reminder, timezone, task.id)
            return redirect('todo_list:tasks')
        else:
            messages.error(request,'Please Fill all the Input Fields')
            return render(request,
                          'todo_list_app/task_update.html',
                          {'task':
                               task, 'categories': categories, 'reminder': reminder, 'form': form})
    else:
        form = TaskForm()
        return render(request,
                      'todo_list_app/task_update.html',
                      {'task':
                           task, 'categories': categories, 'reminder': reminder, 'form': form})
