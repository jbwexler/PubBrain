# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0003_auto_20150328_1152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pubmedsearch',
            name='date_file_saved',
        ),
        migrations.AddField(
            model_name='pubmedsearch',
            name='brain_regions',
            field=models.ManyToManyField(to='pubbrain_app.BrainRegion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pubmedsearch',
            name='last_updated',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pubmedsearch',
            name='date_added',
            field=models.DateField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
