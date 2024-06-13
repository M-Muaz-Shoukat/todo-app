from django.core.exceptions import ObjectDoesNotExist
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
from todo_list_app.permissions import IsOwner
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


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_permissions(self):
        return [IsAuthenticated(), IsOwner(user_path='user')]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Category.objects.filter(name__icontains=query, user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_permissions(self):
        return [IsAuthenticated(), IsOwner(user_path='category.user')]

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
        query_set = self.get_queryset()
        serializer = self.serializer_class(query_set, many=True)
        for data in serializer.data:
            task_id = data['id']
            reminder = Reminder.objects.get(task_id=task_id)
            if reminder:
                data['reminder'] = ReminderSerializer(reminder).data
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

