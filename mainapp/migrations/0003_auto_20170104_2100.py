# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_auto_20170104_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='author',
            field=models.ForeignKey(to='mainapp.Author', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='content',
            name='author',
            field=models.ForeignKey(to='mainapp.Author', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='module',
            name='author',
            field=models.ForeignKey(to='mainapp.Author', blank=True, null=True),
        ),
    ]
