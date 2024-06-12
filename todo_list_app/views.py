from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from todo_list_app.paginations import CustomPagination
from todo_list_app.models import Category, Task, Reminder
from django.db.models import Q
from todo_list_app.utils import send_code_to_user, verify_otp_code
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_bytes, force_str
from todo_list_app.models import User
from rest_framework.generics import GenericAPIView
from todo_list_app.serializers import (UserRegisterSerializer, UserLoginSerializer, LogoutSerializer,
                                       CategorySerializer, ReminderSerializer, TaskSerializer)
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
            return Response({'data': user_data, 'user_id': user_id, 'message': f"hi thanks for signing up passcode"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmailView(GenericAPIView):

    def post(self, request):
        otp_code = request.data.get('code')
        user_id = request.data.get('user_id')
        user_id = int(force_str(urlsafe_base64_decode(user_id)))
        try:
            if not verify_otp_code(otp_code, user_id):
                return Response({
                    'message': 'code is Invalid'
                }, status=status.HTTP_404_NOT_FOUND)
            user = User.objects.get(id=user_id)
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message': 'account email verified successfully!'
                }, status=status.HTTP_200_OK)

            return Response({
                'message': 'code is invalid user already verified!'
            }, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'message': 'passcode not provided'}, status=status.HTTP_404_NOT_FOUND)


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

        return obj.category.user == request.user


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Category.objects.filter(name__icontains=query, user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = CustomPagination

    def get_queryset(self):
        query = self.request.query_params.get('q')
        task_list = Task.objects.filter(category__user=self.request.user)

        if query:
            task_list = task_list.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
        return task_list

    def list(self, request, *args, **kwargs):
        paginator = self.pagination_class()
        query_set = self.get_queryset()
        page = paginator.paginate_queryset(queryset=query_set, request=request)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            serializer = self.serializer_class(query_set, many=True)

        for data in serializer.data:
            task_id = data['id']
            reminder = Reminder.objects.get(task_id=task_id)
            if reminder:
                data['reminder'] = ReminderSerializer(reminder).data
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

