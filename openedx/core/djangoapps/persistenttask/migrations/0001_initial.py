# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FailedTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_name', models.CharField(max_length=255)),
                ('task_id', models.CharField(max_length=255, db_index=True)),
                ('args', jsonfield.fields.JSONField(blank=True)),
                ('kwargs', jsonfield.fields.JSONField(blank=True)),
                ('exc', models.CharField(max_length=255)),
                ('datetime_failed', models.DateTimeField(db_index=True)),
                ('datetime_resolved', models.DateTimeField(default=None, null=True, blank=True)),
            ],
        ),
        migrations.AlterIndexTogether(
            name='failedtask',
            index_together=set([('task_name', 'exc')]),
        ),
    ]
