# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_auto_20170104_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='Curiosity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=128)),
            ],
        ),
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ('additional_text',)},
        ),
        migrations.RemoveField(
            model_name='module',
            name='content',
        ),
        migrations.AlterField(
            model_name='module',
            name='comment',
            field=models.CharField(max_length=1024, blank=True),
        ),
        migrations.AddField(
            model_name='curiosity',
            name='contents',
            field=models.ManyToManyField(to='mainapp.Content'),
        ),
        migrations.AddField(
            model_name='module',
            name='curiosities',
            field=models.ManyToManyField(to='mainapp.Curiosity'),
        ),
    ]
