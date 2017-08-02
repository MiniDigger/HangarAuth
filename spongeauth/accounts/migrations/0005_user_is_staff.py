# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-21 22:03
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    db_alias = schema_editor.connection.alias
    User.objects.using(db_alias).filter(is_admin=True).update(is_staff=True)

def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_create_dummy_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]