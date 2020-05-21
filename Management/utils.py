from Management import models
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


