# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0006_auto_20150401_1124'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brainregion',
            old_name='atlas_voxels',
            new_name='atlas_regions',
        ),
        migrations.RenameField(
            model_name='brainregion',
            old_name='is_atlasregion',
            new_name='has_pkl',
        ),
        migrations.RenameField(
            model_name='brainregion',
            old_name='atlasregions',
            new_name='mapped_regions',
        ),
        migrations.AddField(
            model_name='brainregion',
            name='pkl',
            field=models.CharField(max_length=500, blank=True),
            preserve_default=True,
        ),
    ]
