from django.shortcuts import render, redirect
from apps.Management import models
from django.forms import Form
from django.forms import fields


# Create your views here.


class LoginForm(Form):
    error_messages = {
        "required": "不能为空",
        "max_length": "超过最大长度",
        "min_length": "输入长度不足",
    }
    user = fields.CharField(required=True, max_length=16, error_messages=error_messages)
    password = fields.CharField(required=True, min_length=10, error_messages=error_messages)


def login(request):
    if request.method == "GET":
        return render(request, 'login.html', {"info": "请先登录"})
    else:
        check = LoginForm(request.POST)
        res = check.is_valid()
        if res:
            u = check.cleaned_data['user']
            p = check.cleaned_data['password']
            obj = models.users.objects.filter(user=u, pwd=p).first()
            if obj:
                request.session['user_info'] = {'user_id': obj.id, 'username': u}
                return redirect("/plm/management/hr/")
            return render(request, 'login.html', {"info": "用户名或密码不正确"})
        else:
            return render(request, 'login.html', {"info": "用户名或密码不正确"})


def logout(request):
    if request.session.get('user_info'):
        request.session.clear()
    return redirect('/plm/management/login/')


