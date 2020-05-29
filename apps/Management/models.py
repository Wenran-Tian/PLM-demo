from django.db import models

# Create your models here.
# Human Resource database


class users(models.Model):
    user = models.CharField(max_length=32, unique=True)
    pwd = models.CharField(max_length=64)


class personnel(models.Model):

    pid = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=32)
    choice_list = ((1, "男"), (2, "女"))
    gender = models.IntegerField(choices=choice_list, null=True, default=1)
    status = models.CharField(max_length=32, default="在职")
    rank = models.CharField(max_length=32, default="工程师")
    dep = models.ForeignKey("department",  default=99, null=True, on_delete=models.SET_NULL)


class department(models.Model):
    did = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=48)
    mgr = models.ForeignKey('personnel', null=True, on_delete=models.SET_NULL)


RANK_LIST = ["工程师", "助理工程师", "高级工程师", "暂无"]


# Projects and Tasks database

class Project(models.Model):
    prj_id = models.CharField(max_length=24, unique=True)
    prj_name = models.CharField(max_length=48, default="未定", null=True)
    created_date = models.DateTimeField(null=True)
    start_time = models.DateField(null=True)
    end_time = models.DateField(null=True)
    product_model = models.CharField(max_length=36, unique=True, default="未定", null=True)
    prj_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True)
    status = models.CharField(max_length=32, default="预备", null=True)

    choice_list = ((0, "未开始"), (1, "进行中"), (2, "预警"), (3, "延期"), (4, "取消"), (5, "完成"), (6, "延期完成"))
    condition = models.IntegerField(choices=choice_list, null=True, default=0)
    remark = models.CharField(max_length=200, default="暂无", null=True)

    statement = models.TextField(null=True, max_length=1000)

    created_by = models.ForeignKey('personnel', null=True, on_delete=models.SET_NULL, related_name="creby")
    managed_by = models.ForeignKey('personnel', null=True, on_delete=models.SET_NULL, related_name="mgrby")


CONDITION_LIST = ["未开始", "进行中", "预警", "延期", "取消", "完成", "延期完成"]
CONDITION_DICT = {"未开始": 0, "进行中": 1, "预警": 2, "延期": 3, "取消": 4, "完成": 5, "延期完成": 6}
CONDITION_COLOR_16 = ["#d3d3d3", "#4169e1", "#ffff00", "#ffa500", "#ff0000", "#2fff00", "#008000"]

CONDITION_PROB_LIST = ["未解决", "进行中", "预警", "延期", "取消", "已解决", "延期已解决"]
CONDITION_PROB_DICT = {"未解决": 0, "进行中": 1, "预警": 2, "延期": 3, "取消": 4, "已解决": 5, "延期已解决": 6}

CONDITION_COLOR = ["ganttGray", "ganttBlue", "ganttYellow", "ganttRed", "ganttRed", "ganttGreen", "ganttGreen"]


class Task(models.Model):

    task_name = models.CharField(max_length=48, null=True)
    t_start_time = models.DateField(null=True)
    t_end_time = models.DateField(null=True)
    duration = models.DecimalField(max_digits=6, decimal_places=1, null=True)
    choice_list = ((0, "未开始"), (1, "进行中"), (2, "预警"), (3, "延期"), (4, "取消"), (5, "完成"), (6, "延期完成"))
    condition = models.IntegerField(choices=choice_list, null=True, default=0)
    remark = models.CharField(max_length=100, default="暂无", null=True)
    statement = models.TextField(null=True, max_length=1000)
    task_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True)

    parent_task = models.ForeignKey("Task", null=True, on_delete=models.CASCADE, related_name="parenttask")
    principle = models.ForeignKey("personnel", null=True, on_delete=models.SET_NULL)
    parent_project = models.ForeignKey("Project", on_delete=models.CASCADE)


class PersonToTask(models.Model):
    remark = models.CharField(max_length=100, default="暂无", null=True)
    task = models.ForeignKey("Task", on_delete=models.CASCADE)
    person = models.ForeignKey("personnel", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("task", "person"), ]


class Problem(models.Model):
    prob_title = models.CharField(max_length=48)
    remark = models.CharField(max_length=200, default="暂无", null=True)
    choice_list = ((0, "未开始"), (1, "进行中"), (2, "预警"), (3, "延期"), (4, "取消"), (5, "完成"), (6, "延期完成"))
    condition = models.IntegerField(choices=choice_list, null=True, default=0)

    start_time = models.DateField(null=True)
    expect_end_time = models.DateField(null=True)
    real_end_time = models.DateField(null=True)

    responsible = models.ForeignKey("personnel", on_delete=models.SET_NULL, null=True)
    parent_task = models.ForeignKey("Task", on_delete=models.CASCADE)


class FilePath(models.Model):
    path = models.CharField(max_length=200)
    name = models.CharField(max_length=80)

    parent_task = models.ForeignKey("Task", null=True, on_delete=models.CASCADE)
    parent_project = models.ForeignKey("Project", on_delete=models.CASCADE)
    parent_prob = models.ForeignKey("Problem", null=True, on_delete=models.CASCADE)


""" do not forget this: 
python manage.py makemigrations
python manage.py migrate

"""

prjChartsData = {}
taskChartsData = {}

