# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_auto_20170104_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='module',
            name='finished_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='module',
            name='views_count',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
    ]
