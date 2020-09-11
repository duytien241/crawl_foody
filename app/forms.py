from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'type': 'text',
        'placeholder': 'Họ',
        'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'type': 'text',
        'placeholder': 'Tên',
        'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'type': 'text',
        'placeholder': 'Email',
        'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'type': 'password',
        'placeholder': 'Mật khẩu',
        'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'type': 'password',
        'placeholder': 'Nhập lại mật khẩu',
        'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "Email address already exists."
            )
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        if commit:
            user.username = self.cleaned_data['email']
            user.save()
        return user
