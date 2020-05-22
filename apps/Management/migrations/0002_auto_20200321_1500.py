# Generated by Django 3.0.4 on 2020-03-21 07:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='did',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='dep',
            field=models.ForeignKey(default=99, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apps.Management.department'),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='pid',
            field=models.CharField(max_length=16, unique=True),
        ),
    ]