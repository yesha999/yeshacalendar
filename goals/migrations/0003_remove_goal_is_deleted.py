# Generated by Django 4.0.6 on 2022-08-10 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0002_goal_goalcomment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='is_deleted',
        ),
    ]
