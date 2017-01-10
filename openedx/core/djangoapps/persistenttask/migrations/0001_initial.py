# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FailedTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_name', models.CharField(max_length=255, db_index=True)),
                ('task_id', models.CharField(max_length=255)),
                ('argstring', models.TextField(blank=True)),
                ('kwargstring', models.TextField(blank=True)),
                ('exc', models.CharField(max_length=255)),
                ('datetime_failed', models.DateTimeField()),
                ('datetime_resolved', models.DateTimeField(default=None, null=True, db_index=True, blank=True)),
            ],
        ),
    ]
