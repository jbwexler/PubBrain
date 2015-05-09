# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0011_auto_20150429_1437'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pubmedsearch',
            name='filename',
        ),
        migrations.AddField(
            model_name='pubmedsearch',
            name='file',
            field=models.FileField(null=True, upload_to=b'', blank=True),
            preserve_default=True,
        ),
    ]
