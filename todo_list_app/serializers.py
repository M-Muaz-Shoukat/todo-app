from rest_framework import serializers
from todo_list_app.models import User
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from tokenize import TokenError


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68,min_length=6,write_only=True)
    password2 = serializers.CharField(max_length=68,min_length=6,write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password','')
        password2 = attrs.get('password2','')
        if password != password2:
            raise serializers.ValidationError('Passwords must match')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )

        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68,min_length=6,write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials try again!')

        user_token = user.tokens()

        return {
            'email': user.email,
            'full_name': user.get_full_name,
            'access_token': str(user_token.get('access')),
            'refresh_token': str(user_token.get('refresh')),
        }


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is invalid or has expired!',
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            return self.fail('bad_token')

