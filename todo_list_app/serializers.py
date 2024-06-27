from rest_framework import serializers
from todo_list_app.models import User, Category, Reminder, Task
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

    class Meta:
        model = User
        fields = ['email', 'password']


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


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']


class ReminderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reminder
        fields = ['remind_at', 'is_sent']


class TaskSerializer(serializers.ModelSerializer):
    reminder = ReminderSerializer(required=False, default=None)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'completed', 'category', 'reminder', 'assigned_to']

    def create(self, validated_data):
        request = self.context.get('request')
        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            due_date=validated_data['due_date'],
            completed=validated_data['completed'],
            category=validated_data['category'],
            assigned_to=validated_data['assigned_to'],
        )
        reminder = None
        if validated_data.get('reminder') and validated_data['reminder'].get('remind_at'):
            reminder = Reminder.objects.create(
                user=request.user,
                task=task,
                remind_at=validated_data['reminder'].get('remind_at'),
            )
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date,
            'completed': task.completed,
            'category': task.category,
            'assigned_to': task.assigned_to,
            'reminder': reminder
        }

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.category = validated_data.get('category', instance.category)
        instance.assigned_to = validated_data.get('assigned_to', instance.assigned_to)
        instance.save()
        instance.reminder = Reminder.objects.get(task_id=instance.id)
        reminder_data = validated_data.get('reminder')
        if reminder_data and reminder_data.get('remind_at'):

            if hasattr(instance, 'reminder') and instance.reminder is not None:

                instance.reminder.remind_at = reminder_data.get('remind_at', instance.reminder.remind_at)
                instance.reminder.save()
            else:

                Reminder.objects.create(
                    user=request.user,
                    task=instance,
                    remind_at=reminder_data.get('remind_at')
                )

        return instance



