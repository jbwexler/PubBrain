# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0002_auto_20150109_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='brainregion',
            name='synonyms',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
