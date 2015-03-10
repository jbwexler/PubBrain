# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0006_auto_20150310_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brainregion',
            name='atlas_voxels',
        ),
    ]
