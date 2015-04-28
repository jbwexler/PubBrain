# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0008_auto_20150402_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchtoregion',
            name='side',
            field=models.CharField(max_length=2, choices=[(b'l', b'left'), (b'r', b'right'), (b'u', b'uni'), (b'ul', b'uni-left'), (b'ur', b'uni-right')]),
            preserve_default=True,
        ),
    ]
