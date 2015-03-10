# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0007_remove_brainregion_atlas_voxels'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brainregion',
            old_name='atlas_voxels1',
            new_name='atlas_voxels',
        ),
    ]
