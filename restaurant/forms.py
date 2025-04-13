from django import forms
from .models import Feedback
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comments', 'rating']  # Exclude the username field
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4}),
        }
        

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    class Meta:
        model = User
        fields = ['username', 'email','password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        help_texts = {
            'username': '',  # Removes the help text for the username
        }
    

class PasswordChangeWithOldPasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        user = self.user  # Access the user object from the form instance

        # Check if the old password is correct
        if not user.check_password(old_password):
            raise ValidationError("The old password is incorrect.")
        return old_password
