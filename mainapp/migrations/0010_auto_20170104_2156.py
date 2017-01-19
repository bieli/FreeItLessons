# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0009_module_achievements_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='additional_info',
            field=models.TextField(max_length=256),
        ),
    ]
