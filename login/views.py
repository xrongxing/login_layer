# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from . import models

# Create your views here.

def index(request):
    pass
    return render(request, 'login/index.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        #print(username, password)
        message = '所有字段都必须填写'
        if username and password:
            username = username.strip()
            #password = password.strip()
            #print(username, password)
            try:
                user = models.User.objects.get(name=username)
                if user.password == password:
                    #print('ok')
                    return redirect('/index/')
                else:
                    #print('no,the password: "%s"' % password)
                    message = '密码错误'
            except:
                message = '用户名不存在'
        context = {
            'message': message,
        }
        return render(request, 'login/login.html', context)
    return render(request, 'login/login.html')

def register(request):
    pass
    return render(request, 'login/register.html')

def logout(request):
    pass
    return redirect('/index/')
