# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_auto_20170104_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='achievements_desc',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
