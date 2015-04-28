# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0007_auto_20150401_1627'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brainregion',
            old_name='pkl',
            new_name='left_pkls',
        ),
        migrations.AddField(
            model_name='brainregion',
            name='right_pkls',
            field=models.CharField(max_length=500, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='uni_pkls',
            field=models.CharField(max_length=500, blank=True),
            preserve_default=True,
        ),
    ]
