# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pmid',
            name='title',
            field=models.CharField(default=b'', max_length=1000),
            preserve_default=True,
        ),
    ]
