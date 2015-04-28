# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0002_auto_20150326_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pmid',
            name='abstract',
            field=models.TextField(default=b'', max_length=100000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pmid',
            name='title',
            field=models.CharField(default=b'', max_length=10000),
            preserve_default=True,
        ),
    ]
