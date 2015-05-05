# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0010_auto_20150428_1634'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brainregion',
            old_name='generation',
            new_name='topological_sort',
        ),
    ]
