# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_auto_20170104_1646'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='curiosity',
            options={'ordering': ('title',)},
        ),
        migrations.AddField(
            model_name='curiosity',
            name='author',
            field=models.ForeignKey(blank=True, to='mainapp.Author', null=True),
        ),
    ]
