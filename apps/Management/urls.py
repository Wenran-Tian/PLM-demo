from django.urls import path
from apps.Management import views_Prob
from apps.Management import views_Task, views_HR, views_Prj

urlpatterns = [

    path('hr/', views_HR.hr),
    path('hr/add/', views_HR.hr_add),
    path('hr/del/', views_HR.hr_del),
    path('hr/edit/', views_HR.hr_edit),

    path('department/', views_HR.department),
    path('department/add/', views_HR.department_add),
    path('department/del/', views_HR.department_del),
    path('department/edit/', views_HR.department_edit),

    path('project/', views_Prj.prj),
    path('project/add/', views_Prj.prj_add),
    path('project/del/', views_Prj.prj_del),
    path('project/edit/', views_Prj.prj_edit),

    path('task/select_by_prj/', views_Task.select_by_prj),
    path('task/task_by_prj/', views_Task.task_by_prj),
    path('task/add/', views_Task.task_add),
    path('task/del/', views_Task.task_del),
    path('task/edit/', views_Task.task_edit),
    path('task/inspect/', views_Task.task_inspect),

    path('persontotask/add/', views_Task.persontotask_add),
    path('persontotask/del/', views_Task.persontotask_del),
    path('persontotask/edit/', views_Task.persontotask_edit),

    path('task/select_by_person/', views_Task.select_by_person),
    path('task/task_by_person/', views_Task.task_by_person),

    path('task/add_prob/', views_Task.add_prob),
    path('task/del_prob/', views_Task.del_prob),
    path('task/edit_prob/', views_Task.edit_prob),

    path('upload/', views_Task.upload),
    path('download/', views_Task.download),
    path('delete/', views_Task.delete),

    path('problem/', views_Prob.problem_inspect),

]
