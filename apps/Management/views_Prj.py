from django.shortcuts import render,HttpResponse,redirect
from apps.Management import models
import time
import json
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
def prj(request):
    index = request.GET.get("index")
    if not index:
        index = "prj_id"
    prjdata = models.Project.objects.all().order_by(index).prefetch_related("created_by", "managed_by")
    return render(request, 'management/Project/prj.html', {'prjdata': prjdata})


@login_check
def prj_add(request):
    if request.method == "GET":
        persons = models.personnel.objects.all()
        return render(request, "management/Project/prj_add.html", {"persons": persons})
    else:
        np = {}
        np["prj_name"] = request.POST.get("prj_name")
        np["start_time"] = request.POST.get("start_time")
        np["end_time"] = request.POST.get("end_time")
        np["product_model"] = request.POST.get("product_model")
        try:
            np["prj_budget"] = float(request.POST.get("prj_budget"))
        except:
            np["prj_budget"] = 0
        np["status"] = request.POST.get("status")
        np["created_by_id"] = request.POST.get("created_by_id")
        np["managed_by_id"] = request.POST.get("managed_by_id")
        np["created_date"] = str(time.strftime("%Y-%m-%d %X", time.localtime()))
        np["statement"] = request.POST.get("statement")
        np["remark"] = request.POST.get("remark")
        # print(np)
        models.Project.objects.create(**np)
        # print(np)
        # if np["pid"] == "":
        lp = models.Project.objects.latest('id')
        strid = str(lp.id)
        print('PRJ' + '0'*(5-len(strid)) + strid)
        models.Project.objects.filter(id=lp.id).update(prj_id='PRJ' + '0' * (5 - len(strid)) + strid)
    return redirect('/plm/management/project/')


@login_check
def prj_del(request):
    ret = {"status": True, "msg": None}
    prj_id = request.POST.get("prj_id")
    # print("---------------------")
    # print(prj_id)
    models.Project.objects.filter(prj_id=prj_id).delete()
    return HttpResponse(json.dumps(ret))


@login_check
def prj_edit(request):
    ret = {"status": True, "msg": None}
    if request.method == "GET":
        op_id = request.GET.get('prj_id')
        # print(op_id)
        project = models.Project.objects.filter(prj_id=op_id).values().first()
        # print(ep)
        persons = models.personnel.objects.all()
        time_list = [str(project["start_time"]), str(project["end_time"])]
        return render(request, 'management/Project/prj_edit.html', {"project": project, "persons": persons, "conditions": models.CONDITION_LIST, "time_list": time_list})
    else:
        np = {}
        np["prj_name"] = request.POST.get("prj_name")
        np["start_time"] = request.POST.get("start_time")
        np["end_time"] = request.POST.get("end_time")
        np["product_model"] = request.POST.get("product_model")
        try:
            print()
            np["prj_budget"] = float(request.POST.get("prj_budget"))

        except:
            np["prj_budget"] = 0
        np["status"] = request.POST.get("status")
        np["created_by_id"] = request.POST.get("created_by_id")
        np["managed_by_id"] = request.POST.get("managed_by_id")
        np["statement"] = request.POST.get("statement")
        np["remark"] = request.POST.get("remark")
        op_id = request.POST.get("prj_id")
        # np["pid"] = request.POST.get("pid")
        # print(op_id)
        # print(np)
        models.Project.objects.filter(prj_id=op_id).update(**np)
        return redirect("/plm/management/project/")
