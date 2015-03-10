# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0004_auto_20150220_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brainregion',
            name='children',
        ),
        migrations.AlterField(
            model_name='brainregion',
            name='parents',
            field=models.ManyToManyField(related_name='children', null=True, to='pubbrain_app.BrainRegion', blank=True),
            preserve_default=True,
        ),
    ]
