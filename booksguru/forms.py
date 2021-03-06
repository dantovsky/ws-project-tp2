from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Comment

class SignUpForm(UserCreationForm):
    # email = forms.EmailField()
    first_name = forms.CharField(max_length=75)
    last_name = forms.CharField(max_length=75)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'book_id', 'comment']