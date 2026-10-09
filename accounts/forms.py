from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """注册表单：在 Django 内置注册表单基础上增加邮箱字段。"""
    email = forms.EmailField(
        required=True,
        label='邮箱',
        error_messages={'required': '请输入邮箱地址'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 统一为所有字段添加 Bootstrap 样式
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        """邮箱唯一性校验。"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册，请更换')
        return email
