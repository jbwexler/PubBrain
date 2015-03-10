# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0003_brainregion_synonyms'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brainregion',
            name='parent',
        ),
        migrations.AddField(
            model_name='brainregion',
            name='parents',
            field=models.ManyToManyField(related_name='parents_rel_+', null=True, to='pubbrain_app.BrainRegion', blank=True),
            preserve_default=True,
        ),
    ]
