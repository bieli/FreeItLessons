# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('sort_order', models.PositiveIntegerField(db_index=True, editable=False, default=0)),
                ('level', models.IntegerField(default=1)),
                ('note', models.TextField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('status', models.IntegerField(default=1)),
                ('value', models.TextField(max_length=4000)),
                ('additional_text', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=128)),
                ('comment', models.CharField(max_length=1024)),
                ('sort_order', models.PositiveIntegerField(db_index=True, editable=False, default=0)),
                ('chapter', models.ForeignKey(null=True, to='mainapp.Chapter', blank=True)),
                ('content', models.ForeignKey(null=True, to='mainapp.Content', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='chapter',
            name='content',
            field=models.ForeignKey(null=True, to='mainapp.Content', blank=True),
        ),
    ]
