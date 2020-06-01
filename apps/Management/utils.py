from apps.Management import models
import datetime
date_str = "April 15, 2020"
month_dict= {"January": "1","February":"2","March":"3","April":"4","May":"5",
"June":"6","July":"7","August":"8","September":"9","October":"10","November":"11","December":"12"}


def ifwarning(start, end, now=datetime.datetime.now()):

    dl1 = start.split("-")
    dl2 = end.split("-")
    i = 0
    for i in range(3):
        dl1[i] = int(dl1[i])
        dl2[i] = int(dl2[i])
    t1 = datetime.datetime(dl1[0], dl1[1], dl1[2])
    t2 = datetime.datetime(dl2[0], dl2[1], dl2[2])

    t1 += datetime.timedelta(hours=8)
    t2 += datetime.timedelta(hours=17)

    if (t2-now) < (t2-t1)*0.15:
        return True


def ifoutoftime(end, now):
    dl2 = end.split("-")
    for i in range(3):
        dl2[i] = int(dl2[i])
    t2 = datetime.datetime(dl2[0], dl2[1], dl2[2], hour=17)
    if now > t2:
        print("end time is", t2)
        print("now time is", now)
        return True


def datetransformer(date):
    print(date)
    s = date.split(' ')
    # return s[2] + "-" + month_dict[s[0]] + '-' + s[1][0:-1]
    return "0000-00-00"

# print(datetransformer(date_str))


def stringdatedifference(datesting1, datesting2):
    """ only for YYYY-MM-DD
    :param datesting1:
    :param datesting2:
    :return:
    """
    dl1 = datesting1.split("-")
    dl2 = datesting2.split("-")
    i = 0
    for i in range(3):
        dl1[i] = int(dl1[i])
        dl2[i] = int(dl2[i])
    t1 = datetime.datetime(dl1[0], dl1[1], dl1[2])
    t2 = datetime.datetime(dl2[0], dl2[1], dl2[2])
    interval = t2 - t1
    return interval.days+1


def todayindaterange(start, end, now=datetime.datetime.now()):
    """ only for YYYY-MM-DD
    :return:
    """
    dl1 = start.split("-")
    dl2 = end.split("-")
    i = 0
    for i in range(3):
        dl1[i] = int(dl1[i])
        dl2[i] = int(dl2[i])
    t1 = datetime.datetime(dl1[0], dl1[1], dl1[2])
    t2 = datetime.datetime(dl2[0], dl2[1], dl2[2], 23)

    if t1 > t2:
        buff = t1
        t1 = t2
        t2 = buff

    result = 0
    if t2 < now:
        result = 5
    elif t1 < now:
        result = 1
    return result


def auto_condition_update(project_id):
    tasks = models.Task.objects.filter(parent_project_id=project_id)
    now = datetime.datetime.now()
    for task in tasks:
        start = str(task.t_start_time)
        end = str(task.t_end_time)
        if not (task.condition in (5, 6)) and ifoutoftime(end, now):
            models.Task.objects.filter(id=task.id).update(condition=3)
        if task.condition == 1 and ifwarning(start, end, now):
            models.Task.objects.filter(id=task.id).update(condition=2)
        elif task.condition == 0 and datetime.datetime(year=task.t_start_time.year, month=task.t_start_time.month, day=task.t_start_time.day) < now:
            models.Task.objects.filter(id=task.id).update(condition=1)
        # print(datetime.datetime(year=task.t_start_time.year, month=task.t_start_time.month, day=task.t_start_time.day))
    # print("condition updated")


def get_month_range(start_day,end_day):
    """
    :param start_day:
    :param end_day:
    :return: a list of string of months between start_day and end_day
    """
    months = (end_day.year - start_day.year)*12 + end_day.month - start_day.month
    month_range = ['%s-%s'%(start_day.year + mon//12,mon%12+1)
                    for mon in range(start_day.month-1,start_day.month + months)]
    return month_range


def update_prj_charts():
    data = {}
    data["labels"] = []
    data["colors"] = []
    data["counts"] = []
    for i in range(len(models.CONDITION_LIST)):
        count = models.Project.objects.filter(condition=i).count()
        if count != 0:
            data["labels"].append(models.CONDITION_LIST[i])
            data["counts"].append(count)
            data["colors"].append(models.CONDITION_COLOR_16[i])
        data["length"] = len(data["labels"])

    prjs = models.Project.objects.order_by("start_time")
    times_prjs = {}
    for prj in prjs:
        time_series = get_month_range(prj.start_time, prj.end_time)
        for time in time_series:
            if time in times_prjs:
                times_prjs[time] += 1
            else:
                times_prjs[time] = 1

    data["months"] = []
    for key in times_prjs.keys():
        data["months"].append(key)
    data["prjs"] = []
    for value in times_prjs.values():
        data["prjs"].append(value)

    models.prjChartsData = data


def update_task_charts():
    data = {}
    data["labels"] = []
    data["colors"] = []
    data["counts"] = []
    for i in range(7):
        count = models.Task.objects.filter(condition=i).count()
        if count != 0:
            data["labels"].append(models.CONDITION_LIST[i])
            data["counts"].append(count)
            data["colors"].append(models.CONDITION_COLOR_16[i])
        data["length"] = len(data["labels"])

    tasks = models.Task.objects.order_by("t_start_time")
    times_tasks = {}
    for task in tasks:
        time_series = get_month_range(task.t_start_time, task.t_end_time)
        for time in time_series:
            if time in times_tasks:
                times_tasks[time] += 1
            else:
                times_tasks[time] = 1

    data["months"] = []
    for key in times_tasks.keys():
        data["months"].append(key)
    data["tasks"] = []
    for value in times_tasks.values():
        data["tasks"].append(value)

    data["dep_charts"] = []
    ptt = models.PersonToTask.objects.prefetch_related("task", "task__parent_project", "person", "person__dep").order_by("person__dep_id")
    tasks_num = ptt.count()

    for j in range(5):
        ptt_ds = ptt.filter(person__dep_id=j+1).all()
        count = ptt_ds.count()
        dep_dict = {}

        if count != 0:
            dep_dict['name'] = ptt_ds[0].person.dep.title
            print(dep_dict['name'])
            dep_dict["labels"] = []
            dep_dict["counts"] = []
            dep_dict["colors"] = []
            dep_dict["tasks"] = count
            for i in range(len(models.CONDITION_LIST)):
                count = ptt_ds.filter(task__condition=i).count()
                if count != 0:
                    dep_dict["labels"].append(models.CONDITION_LIST[i])
                    dep_dict["counts"].append(count)
                    dep_dict["colors"].append(models.CONDITION_COLOR_16[i])
                dep_dict["length"] = len(dep_dict["labels"])

        data["dep_charts"].append(dep_dict)

        # print(data["dep_charts"][j])


    # data["dep_condition"] = []
    # persons = models.personnel.objects.order_by("dep")
    # dep_id = -1
    # for person in persons:
    #     person_manage_task = person.task_set.all()
    #     if person_manage_task :
    #         if dep_id != person.dep_id:
    #             data0 = {}
    #             dep_id = person.dep_id
    #         data0["labels"].append(models.CONDITION_LIST[i])
    #         data0["counts"].append(count)
    #         data0["colors"].append(models.CONDITION_COLOR_16[i])

    models.depChartsData = data["dep_charts"]
    models.taskChartsData = data


update_prj_charts()
update_task_charts()
