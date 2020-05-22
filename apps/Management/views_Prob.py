from django.shortcuts import render
from apps.Management import models


def problem_inspect(request):
    prob_id = int(request.GET.get("prob_id"))
    problem = models.Problem.objects.filter(id=prob_id).prefetch_related("parent_task", "responsible", "parent_task__parent_project").first()
    project_name = problem.parent_task.parent_project.prj_name
    task_name = problem.parent_task.task_name
    prob_title = problem.prob_title




    return render(request, "management/Task/problem_inspect.html", {"problem": problem})



