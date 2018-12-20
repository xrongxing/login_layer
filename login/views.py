# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from . import models
from . import forms
import hashlib
# Create your views here.

def index(request):
    pass
    return render(request, 'login/index.html')

def login(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        #username = request.POST.get('username', None)
        #password = request.POST.get('password', None)
        #print(username, password)
        #message = '所有字段都必须填写'
        #if username and password:
            #username = username.strip()
            #password = password.strip()
            #print(username, password)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                #if user.password == password:
                if user.password == hash_code(password):
                    #print('ok')
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    #print('no,the password: "%s"' % password)
                    message = '密码错误'
            except:
                message = '用户名不存在'
        else:
            message = '所有字段都必须填写正确'
        #context = {
        #    'message': message,
        #}
        return render(request, 'login/login.html', locals())
    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())

def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        #message = '所有字段都必须填写正确'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 == password2:
                same_name_user = models.User.objects.filter(name=username)
                # 用户名唯一
                if same_name_user:
                    message = '用户名已存在!'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经注册!'
                    return render(request, 'login/register.html', locals())
                new_user = models.User()
                new_user.name = username
                #new_user.password = password1
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')
            else:
                message = '二次密码不一致'
                return render(request, 'login/register.html', locals())
        else:
            message = '所有字段都必须填写正确'
            return render(request, 'login/register.html', locals())

    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/index/')
    request.session.flush()
    # 或者精确删除
    #del request.session['is_login']
    #del request.session['user_id']
    #del request.session['user_name']
    return redirect('/index/')

# 利用hashlib加密密码，并使密码加盐
def hash_code(s, salt='login_layer'):
    h = hashlib.sha256()
    s += salt
    # 与上等同
    #s = s + salt
    # update方法只接受bytes类型
    h.update(s.encode())
    return h.hexdigest()
