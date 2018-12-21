# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from . import models
from . import forms
import hashlib
import datetime
from django.conf import settings
# Create your views here.

def index(request):
    pass
    return render(request, 'login/index.html')

def login(request):
    if request.session.get('is_login', None):
        # 如果状态为已经登陆，进入该url会跳转到index页面
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
                if not user.has_confirmed:
                    message = '账户未激活,请到注册邮箱激活！'
                else:
                    #if user.password == password:
                    # 匹配数据库中存储的密码和使用hash_code()加密后的表单中输入的密码是否一致
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
        # 已经登陆状态不允许注册
        return redirect('/index/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        #message = '所有字段都必须填写正确'

        # 验证表单数据，captcha也会被is_valid()验证
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

                # 条件都满足后开始创建用户
                new_user = models.User()
                new_user.name = username
                #new_user.password = password1
                # 使用加密密码
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirmed_string(new_user)
                send_mail(email, code)
                #return redirect('/login/')
                message = '账户已经注册，请前往注册邮箱验证！'
                return render(request, 'login/confirm.html', locals())
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
        # 如果未登陆，进入此url将跳转到index页面
        return redirect('/index/')
    # 使用session.flush()，admin后台登陆状态也会清除
    #request.session.flush()
    # 或者精确删除
    del request.session['is_login']
    del request.session['user_id']
    del request.session['user_name']
    return redirect('/index/')

# 利用hashlib加密密码，并使密码加盐
def hash_code(s, salt='login_layer'):
    h = hashlib.sha256()
    s += salt
    #print(s)
    # 与上等同
    #s = s + salt
    # update方法只接受bytes类型
    h.update(s.encode())
    return h.hexdigest()

def make_confirmed_string(user):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:S')
    #code = hash_code(user.name, now)
    # 中文用户名先转换，hash_code函数中的h.update()函数不支持，不能用中文用户名注册
    #code = hash_code(user.name.encode('utf-8'), now)
    # 使用固定字符，解决中文用户名注册问题，数据库中查看,ConfirmString中的code字段每次也会是不一样的值
    code = hash_code(u'user.name', now)
    # u'user.name'，打印出来还是'user.name'，不会是user对象的name的值，但生成的code每次都会不同，因为now的时间是变动的
    #print(u'user.name')
    models.ConfirmString.objects.create(code=code, user=user,)
    return code

def send_mail(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = 'Subject Test'
    text_message = '''欢迎注册!'''
    html_message = '''<p>欢迎注册</p>
         <p><a href={}/confirm/?code={} target=blank>请验证，</a></p>
        <p>有效期为{}</p>
        '''.format('http://192.168.1.209:58013', code, settings.CONFIRMED_DAY)
    msg = EmailMultiAlternatives(subject, text_message, settings.EMAIL_HOST_USER, [email,])
    msg.attach_alternative(html_message, 'text/html')
    msg.send()

def user_confirm(request):
    if request.GET.get('code', None):
        code = request.GET.get('code', None)
        message = '错误'
        try:
            confirm = models.ConfirmString.objects.get(code=code)
        except:
            message = '未知确认码！'
            return render(request, 'login/confirm.html', locals())
        c_time = confirm.c_time
        now = datetime.datetime.now()
        if now > c_time + datetime.timedelta(settings.CONFIRMED_DAY):
            message = '过期，请重新注册'
            confirm.user.delete()
            # delete后不要save
            #confirm.user.save()
            # OnToOneField对象，删除user对象后，confirm自动删除，无须再delete
            #confirm.delete()
            #confirm.save()
            return render(request, 'login/confirm.html', locals())
        else:
            confirm.user.has_confirmed = True
            confirm.user.save()
            confirm.delete()
            # delete后不要save
            #confirm.save()
            message = '确认完成，请登陆'
        return render(request, 'login/confirm.html', locals())
    else:
        return redirect('/index/')
