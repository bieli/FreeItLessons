# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_auto_20170104_1600'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ('title',)},
        ),
        migrations.RemoveField(
            model_name='chapter',
            name='content',
        ),
        migrations.RemoveField(
            model_name='module',
            name='chapter',
        ),
        migrations.AddField(
            model_name='chapter',
            name='contents',
            field=models.ManyToManyField(to='mainapp.Content'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='name',
            field=models.CharField(max_length=128, blank=True),
        ),
        migrations.AddField(
            model_name='module',
            name='contents',
            field=models.ManyToManyField(to='mainapp.Chapter'),
        ),
    ]
