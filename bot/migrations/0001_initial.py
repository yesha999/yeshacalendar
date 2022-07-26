# Generated by Django 4.0.6 on 2022-08-29 20:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TgUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_chat_id', models.BigIntegerField(verbose_name='Телеграм чат id')),
                ('tg_user_id', models.BigIntegerField(verbose_name='Телеграм юзер id')),
                ('tg_username', models.CharField(blank=True, default=None, max_length=512, null=True, verbose_name='Телеграм username')),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Связанный пользователь')),
            ],
            options={
                'verbose_name': 'Телеграм Юзер',
                'verbose_name_plural': 'Телеграм Юзеры',
            },
        ),
    ]
