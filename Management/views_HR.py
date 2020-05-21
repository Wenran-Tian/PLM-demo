from django.shortcuts import render,HttpResponse,redirect
from Management import models
import json
from django.forms import Form
from django.forms import fields
from functools import wraps
# Create your views here.


def login_check(func):
    @wraps(func)
    def with_login_check(request):
        try:
            # print('____decorate____')
            v = request.session.get("user_info").get('user_id')
            if not v:
                return redirect("/plm/management/login/")
        except:
            return redirect("/plm/management/login/")
        return func(request)
    return with_login_check


@login_check
def hr(request):
    # print('____hr func____')
    index = request.GET.get("index")
    if not index:
        index = "pid"
    if index == "name":
        hrdata = models.personnel.objects.raw(""" select * from management_personnel order by CONVERT(name using gbk); """)
    else:
        hrdata = models.personnel.objects.all().order_by(index).prefetch_related('dep')
    return render(request, 'management/HR/hr.html', {'hrdata': hrdata})


@login_check
def hr_add(request):
    if request.method == "GET":
        deps = models.department.objects.all()
        return render(request, "management/HR/hr_add.html", {"deps": deps, "ranks": models.RANK_LIST})
    else:
        np = {}
        np["name"] = request.POST.get("name")
        np["gender"] = request.POST.get("gender")
        np["dep_id"] = request.POST.get("department")
        np["rank"] = request.POST.get("rank")
        np["status"] = request.POST.get("status")
        # np["pid"] = request.POST.get("pid")
        models.personnel.objects.create(**np)
        # print(np)
        # if np["pid"] == "":
        lp = models.personnel.objects.latest('id')
        strid = str(lp.id)
        models.personnel.objects.filter(id=lp.id).update(pid='P' + '0'*(3-len(strid)) + strid)
    return redirect('/plm/management/hr/')


@login_check
def hr_del(request):
    ret = {"status": True, "msg": None}
    op_id = request.POST.get('pid')
    # print(op_id)
    models.personnel.objects.filter(pid=op_id).delete()
    return HttpResponse(json.dumps(ret))


@login_check
def hr_edit(request):
    ret = {"status": True, "msg": None}
    if request.method == "GET":
        op_id = request.GET.get('pid')
        # print(op_id)
        ep = models.personnel.objects.filter(pid=op_id).values().first()
        # print(ep)
        deps = models.department.objects.all()
        return render(request,'management/HR/hr_edit.html', {"ep": ep, "deps": deps, "ranks": models.RANK_LIST})
    else:
        np = {}
        np["name"] = request.POST.get("name")
        np["gender"] = request.POST.get("gender")
        np["dep_id"] = request.POST.get("department")
        np["rank"] = request.POST.get("rank")
        np["status"] = request.POST.get("status")
        op_id = request.POST.get("id")
        # np["pid"] = request.POST.get("pid")
        # print(op_id)
        # print(np)
        models.personnel.objects.filter(id=op_id).update(**np)
        return redirect("/plm/management/hr/")


"""
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
"""

@login_check
def department(request):

    # dep_data = models.department.objects.all().values().prefetch_related('mgr')
    depdata = models.department.objects.exclude(id=99).prefetch_related('mgr')  # drop the last department
    return render(request, 'management/HR/department.html', {"depdata": depdata})


@login_check
def department_add(request):
    if request.method == "GET":
        persons = models.personnel.objects.all()
        return render(request, "management/HR/department_add.html", {"persons": persons})
    else:
        nd = {}
        nd["title"] = request.POST.get("title")
        nd["mgr_id"] = int(request.POST.get("mgr_id"))
        # print(nd)
        models.department.objects.create(**nd)
        ld = models.department.objects.exclude(did="D99").latest('id')
        strid = str(ld.id)
        models.department.objects.filter(id=ld.id).update(did='D' + '0'*(2-len(strid)) + strid)
    return redirect('/plm/management/department/')


@login_check
def department_del(request):
    ret = {"status": True, "msg": None}
    op_id = request.POST.get('did')
    # print(op_id)
    models.department.objects.filter(did=op_id).delete()
    return HttpResponse(json.dumps(ret))


@login_check
def department_edit(request):
    # ret = {"status": True, "msg": None}
    if request.method == "GET":
        op_id = request.GET.get('did')
        # print(op_id)
        ed = models.department.objects.filter(did=op_id).values().first()
        # print(ed)
        persons = models.personnel.objects.all()
        return render(request, 'management/HR/department_edit.html', {"ed": ed, "persons": persons})
    else:
        nd = {}
        nd["title"] = request.POST.get("title")
        nd["mgr_id"] = request.POST.get("mgr_id")
        op_id = request.POST.get("id")
        # np["pid"] = request.POST.get("pid")
        # print(op_id)
        # print(np)
        models.department.objects.filter(id=op_id).update(**nd)
        return redirect("/plm/management/department/")
