# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import CaptchaField
class UserForm(forms.Form):
    username = forms.CharField(label='用户名:', max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='密码:', max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # captcha 未找到有什么可用的窗口部件
    #captcha = CaptchaField(label='验证码:', widget=forms.CaptchaInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码:')
