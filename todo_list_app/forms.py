from django import forms
from todo_list_app.models import User
from django.contrib.auth.forms import UserCreationForm
from todo_list_app.models import Category, Task


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'completed', 'category']
