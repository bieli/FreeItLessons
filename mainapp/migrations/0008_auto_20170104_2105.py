# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_auto_20170104_1700'),
    ]

    operations = [
        migrations.RenameField(
            model_name='module',
            old_name='enabled',
            new_name='is_enabled',
        ),
        migrations.AddField(
            model_name='author',
            name='blog_link',
            field=models.CharField(null=True, max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='author',
            name='external_link',
            field=models.CharField(null=True, max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='author',
            name='image_link',
            field=models.CharField(null=True, max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='author',
            name='is_public_mentor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='author',
            name='linkedin_link',
            field=models.CharField(null=True, max_length=256, blank=True),
        ),
    ]
