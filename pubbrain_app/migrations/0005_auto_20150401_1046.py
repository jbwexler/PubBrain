# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0004_auto_20150401_1021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pubmedsearch',
            name='brain_regions',
        ),
        migrations.AddField(
            model_name='pubmedsearch',
            name='left_brain_regions',
            field=models.ManyToManyField(related_name='left_searches', null=True, to='pubbrain_app.BrainRegion', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pubmedsearch',
            name='right_brain_regions',
            field=models.ManyToManyField(related_name='right_searches', null=True, to='pubbrain_app.BrainRegion', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pubmedsearch',
            name='uni_brain_regions',
            field=models.ManyToManyField(related_name='uni_searches', null=True, to='pubbrain_app.BrainRegion', blank=True),
            preserve_default=True,
        ),
    ]
