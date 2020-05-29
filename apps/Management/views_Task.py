from django.shortcuts import render, redirect, HttpResponse
from apps.Management import utils, models
import json,os


def select_by_prj(request):
    projects = models.Project.objects.all().values()
    # print(projects)
    return render(request, "management/Task/project_select.html", {"projects": projects})


def task_by_prj(request):
    if request.method == "GET":
        id = str(request.GET.get("pid"))
        # print(id)
    else:
        id = request.POST.get("project")
        if request.POST.get("update"):
            # print("condition 123")
            utils.auto_condition_update(id)
            utils.update_task_charts()
            ret = {"status": True, "msg": None}
            return HttpResponse(json.dumps(ret))

    project = models.Project.objects.filter(id=id).prefetch_related("managed_by").first()
    tasks = models.Task.objects.filter(parent_project_id=id, parent_task=None).prefetch_related("parent_task")
    gantt_tasks = models.Task.objects.filter(parent_project_id=id).order_by("task_name").prefetch_related('principle')
    sources_string = "["
    for task in gantt_tasks:
        source = "{"
        source += "name:" + '"' + task.task_name + '"' + ','

        try:
            source += "desc:" + '"' + task.principle.name + '"' + ','
        except:
            source += "desc:" + '"' + "暂无备注" + '"' + ','
        values = "values :[{"
        values += "from:" + '"' + str(task.t_start_time) + '"' + ','
        values += "to:" + '"' + str(task.t_end_time) + '"' + ','
        values += "label:" + '"' + task.task_name + '"' + ','
        values += "customClass:" + '"' + models.CONDITION_COLOR[task.condition] + '"' + ','
        values += "}]"

        source += values + "}"
        sources_string += source + ','
    sources_string += "]"
    # print(sources_string)

    return render(request, "management/Task/task_by_prj.html", {"tasks": tasks, "project": project, "gantt_sources":sources_string})


def task_inspect(request):
    if request.method == "GET":
        id = request.GET.get("tid")
        # print(id)
        task = models.Task.objects.filter(id=int(id)).prefetch_related("parent_task", "principle", "parent_project").first()
        # print(task.)
        relations = models.PersonToTask.objects.filter(task_id=id).prefetch_related("person")
        persons = models.personnel.objects.all().raw(""" select * from management_personnel order by CONVERT(name using gbk); """)
        problems = models.Problem.objects.filter(parent_task_id=int(id)).prefetch_related("responsible")
        # try:
        #     path = FILE_BASE + task.parent_project.prj_name + '/' + task.task_name
        #     file_list = []
        #     files = os.listdir(path)
        #     for i in files:
        #         file_list.append(i)
        # except:
        #     file_list = None

        files = models.FilePath.objects.filter(parent_task_id=task.id)
        return render(request, "management/Task/task_inspect.html", {"task": task, "relations": relations, "persons": persons, "problems": problems, "conditions": models.CONDITION_PROB_LIST, "files": files})

    else:
        return HttpResponse("function set")


def task_add(request):
    if request.method == "GET":
        if not request.GET.get("pid"):
            parent_id = request.GET.get("tid")
            pid = (models.Task.objects.filter(id=parent_id).first()).parent_project_id
        else:
            pid = request.GET.get("pid")
            parent_id = None
        if parent_id:
            parent_task = (models.Task.objects.filter(id=parent_id).first())
        else:
            parent_task = None
        persons = models.personnel.objects.raw(""" select * from management_personnel order by CONVERT(name using gbk); """)
        project = models.Project.objects.filter(id=pid).first()
        return render(request, "management/Task/task_add.html", {"project": project, "persons": persons, "conditions": models.CONDITION_LIST, "parent_task": parent_task, "id_info":[pid, parent_id]})
    else:
        nt = {}
        nt["task_name"] = request.POST.get("task_name")
        try:
            nt["t_start_time"] = request.POST.get("t_start_time")
            nt["t_end_time"] = request.POST.get("t_end_time")
            # start_list = nt["t_start_time"].split('-')
            # d1 = datetime.datetime()
            nt["duration"] = utils.stringdatedifference(nt["t_start_time"], nt["t_end_time"])
        except:
            nt["t_start_time"] = None
            nt["t_end_time"] = None
            nt["duration"] = None
        nt["condition"] = models.CONDITION_DICT[request.POST.get("condition")]
        if request.POST.get("remark") == "":
            nt["remark"] = "暂无"
        else:
            nt["remark"] = request.POST.get("remark")
        nt["statement"] = request.POST.get("statement")
        try:
            nt["task_budget"] = int(request.POST.get("task_budget"))
        except:
            nt["task_budget"] = 0

        #print(type(request.POST.get("parent_task_id")))
        try:
            nt["parent_task_id"] = int(request.POST.get("parent_task_id"))
        except:
            nt["parent_task_id"] = None
        nt["principle_id"] = int(request.POST.get("principle_id"))
        nt["parent_project_id"] = int(request.POST.get("parent_project_id"))
        parent_project_id = nt["parent_project_id"]

        print(nt)
        models.Task.objects.create(**nt)
        ntask = models.Task.objects.latest('id')
        models.PersonToTask.objects.create(remark="负责人", task_id=ntask.id, person_id=ntask.principle_id)

        utils.update_task_charts()
        url = (f"""/plm/management/task/task_by_prj?pid={parent_project_id}""")
    return redirect(url)
    # return HttpResponse("123456")


def task_del(request):
    task_id = request.GET.get("tid")
    # print(task_id)
    task = models.Task.objects.filter(id=task_id).prefetch_related("parent_project").first()
    project_id = task.parent_project.id
    models.Task.objects.filter(id=task_id).delete()
    utils.update_task_charts()
    url = f"""/plm/management/task/task_by_prj?pid={project_id}"""
    return redirect(url)


def task_edit(request):
    if request.method == "GET":
        id = request.GET.get("tid")
        # print(id)
        task = models.Task.objects.filter(id=int(id)).prefetch_related("parent_task", "principle", "parent_project").first()

        if task.parent_task:
            parent_task = task.parent_task
        else:
            parent_task = None
        persons = models.personnel.objects.all().values()
        project = models.Project.objects.filter(id=task.parent_project_id).first()
        return render(request, "management/Task/task_edit.html", {"project": project, "persons": persons, "conditions": models.CONDITION_LIST,
                                                                  "parent_task": parent_task, "task": task, "se_time": [str(task.t_start_time), str(task.t_end_time)],
                                                                  "now_condition": models.CONDITION_LIST[task.condition]})
    else:
        nt = {}
        nt["task_name"] = request.POST.get("task_name")
        try:
            nt["t_start_time"] = request.POST.get("t_start_time")
            nt["t_end_time"] = request.POST.get("t_end_time")
            # start_list = nt["t_start_time"].split('-')
            # d1 = datetime.datetime()
            nt["duration"] = utils.stringdatedifference(nt["t_start_time"], nt["t_end_time"])
        except:
            nt["t_start_time"] = None
            nt["t_end_time"] = None
            nt["duration"] = None
        nt["condition"] = models.CONDITION_DICT[request.POST.get("condition")]
        nt["remark"] = request.POST.get("remark")
        nt["statement"] = request.POST.get("statement")
        try:
            nt["task_budget"] = float(request.POST.get("task_budget"))
        except:
            nt["task_budget"] = 0

        nt["principle_id"] = int(request.POST.get("principle_id"))
        parent_project_id = request.POST.get("parent_project_id")
        task_id = request.POST.get("task_id")
        print(task_id)
        print(nt)
        # models.Task.objects.create(**nt)
        # ntask = models.Task.objects.latest('id')
        task = models.Task.objects.filter(id=task_id).first()
        if not (nt["principle_id"] == task.principle_id):
            models.PersonToTask.objects.filter(remark="负责人", task_id=task_id).update(person_id=nt["principle_id"])

        models.Task.objects.filter(id=task_id).update(**nt)
        utils.update_task_charts()
        url = (f"""/plm/management/task/task_by_prj?pid={parent_project_id}""")
    return redirect(url)


def persontotask_add(request):
    ret = {"status": True, "msg": None}
    # print(request.POST.get("person_slc"))
    # print(request.POST.get("remark"))
    # print(request.POST.get("task_id"))
    person_id = int(request.POST.get("person_slc"))
    task_id = int(request.POST.get("task_id"))
    remark = request.POST.get("remark")
    try:
        models.PersonToTask.objects.create(person_id=person_id, task_id=task_id, remark=remark)
    except:
        ret["status"] = False
        ret['msg'] = "人员已存在"

    return HttpResponse(json.dumps(ret))


def persontotask_del(request):
    ret = {"status": True, "msg": None}
    person_id = int(request.POST.get("person_slc"))
    # print(request.POST.get("remark"))
    task_id = int(request.POST.get("task_id"))
    models.PersonToTask.objects.filter(person_id=person_id, task_id=task_id).delete()

    return HttpResponse(json.dumps(ret))


def persontotask_edit(request):
    ret = {"status": True, "msg": None}
    person_id = int(request.POST.get("person_slc"))
    remark = request.POST.get("remark")
    task_id = int(request.POST.get("task_id"))

    # print(person_id, remark, task_id)
    models.PersonToTask.objects.filter(person_id=person_id, task_id=task_id).update(remark=remark)

    return HttpResponse(json.dumps(ret))


def select_by_person(request):
    persons = models.personnel.objects.all().order_by('dep').prefetch_related('dep')
    # print(persons)
    return render(request, "management/Task/person_select.html", {"persons": persons})


def task_by_person(request):
    if request.method == "GET":
        pid = request.GET.get("pid")
        person = models.personnel.objects.filter(id=pid).first()
        ptt = models.PersonToTask.objects.filter(person_id=pid).prefetch_related("task", "task__parent_project", "person")
        ptt_executing = ptt.filter(person_id=pid, task__condition__gt=0, task__condition__lt=4).order_by('task__parent_project', 'task__task_name')
        ptt_notstart = ptt.filter(person_id=pid, task__condition=0).order_by('task__parent_project', 'task__task_name')
        ptt_finished = ptt.filter(person_id=pid, task__condition__in=[5, 6]).order_by('task__parent_project', 'task__task_name')
        return render(request, "management/Task/task_by_person.html", {"person": person,
                                                                       "ptt_executings": ptt_executing,
                                                                       "ptt_notstarts": ptt_notstart,
                                                                       "ptt_finisheds": ptt_finished,
                                                                       })
    else:
        pid = int(request.POST.get("pid"))
        ptt = models.PersonToTask.objects.filter(person_id=pid).prefetch_related("task", "task__parent_project",
                                                                                 "person")
        data = {}
        data["labels"] = []
        data["counts"] = []
        data["colors"] = []
        for i in range(len(models.CONDITION_LIST)):
            count = ptt.filter(task__condition=i).count()
            if count != 0:
                data["labels"].append(models.CONDITION_LIST[i])
                data["counts"].append(count)
                data["colors"].append(models.CONDITION_COLOR_16[i])
            data["length"] = len(data["labels"])

        return HttpResponse(json.dumps(data))


def add_prob(request):
    ret = {"status": True, "msg": None}

    new_prob = {}
    new_prob["parent_task_id"] = int(request.POST.get("task_id"))
    new_prob["prob_title"] = request.POST.get("prob_title")
    new_prob["remark"] = request.POST.get("remark")
    new_prob["condition"] = models.CONDITION_PROB_DICT[request.POST.get("condition")]
    new_prob["responsible_id"] = int(request.POST.get("responsible"))
    # try:
    #     models.Problem.objects.create(new_prob)
    # except Exception as e:
    #     ret["status"] = False
    #     ret["msg"] = str(e)
    models.Problem.objects.create(**new_prob)
    return HttpResponse(json.dumps(ret))


def del_prob(request):
    ret = {"status": True, "msg": None}

    prob_id = int(request.POST.get("prob_id"))
    print(prob_id)

    models.Problem.objects.filter(id=prob_id).delete()
    return HttpResponse(json.dumps(ret))


def edit_prob(request):
    ret = {"status": True, "msg": None}

    edit_prob = {}
    prob_id = int(request.POST.get("prob_id"))
    edit_prob["prob_title"] = request.POST.get("prob_title")
    edit_prob["remark"] = request.POST.get("remark")
    edit_prob["condition"] = models.CONDITION_PROB_DICT[request.POST.get("condition")]
    edit_prob["responsible_id"] = int(request.POST.get("responsible_id"))
    # try:
    #     models.Problem.objects.create(new_prob)
    # except Exception as e:
    #     ret["status"] = False
    #     ret["msg"] = str(e)
    # print(edit_prob)
    models.Problem.objects.filter(id=prob_id).update(**edit_prob)
    return HttpResponse(json.dumps(ret))


FILE_BASE = 'D:/plm/'


def upload(request):

    myFile = request.FILES.get("myfile", None)  # 获取上传的文件，如果没有文件，则默认为None
    if not myFile:
        return HttpResponse("没有文件上传!")
    parent_task_id = int(request.POST.get("task_id"))
    task = models.Task.objects.filter(id=parent_task_id).prefetch_related("parent_project").first()
    parent_project_id = task.parent_project_id
    parent_project_name = task.parent_project.prj_name

    path = FILE_BASE + parent_project_name + '/' + task.task_name

    # + '/' + myFile.name
    newFP = {}
    newFP["path"] = path
    newFP["name"] = myFile.name
    newFP["parent_task_id"] = parent_task_id
    newFP["parent_project_id"] = parent_project_id

    models.FilePath.objects.create(**newFP)
    # destination=open(os.path.join('upload',myFile.name),'wb+')

    try:
        destination = open(os.path.join(path, myFile.name), 'wb+')  # 打开特定的文件进行二进制的写操作
    except:
        os.mkdir(path)
        destination = open(os.path.join(path, myFile.name), 'wb+')  # 打开特定的文件进行二进制的写操作
    for chunk in myFile.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()
    return redirect(f"/plm/management/task/inspect?tid={parent_task_id}")


def download(request):
    fid = request.GET.get("fid")
    fp = models.FilePath.objects.filter(id=fid).first()
    file = open(fp.path + '/' + fp.name, 'rb')
    response = HttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = f'attachment;filename="\\{fp.name}"'
    return response


def delete(request):
    file_id = int(request.POST.get("del_fid"))
    task_id = int(request.POST.get("task_id"))

    file = models.FilePath.objects.filter(id=file_id).first()
    dir = file.path + "/" + file.name

    print(dir, task_id)

    os.remove(dir)
    file.delete()
    ret = {"status": True, "msg": None}
    return HttpResponse(json.dumps(ret))

