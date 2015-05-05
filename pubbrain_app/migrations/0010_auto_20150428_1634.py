# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0009_auto_20150402_1534'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brainregion',
            name='parents',
        ),
        migrations.AddField(
            model_name='brainregion',
            name='FMA_name',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='NIF_name',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='Uberon_name',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='allParents',
            field=models.ManyToManyField(related_name='allChildren', null=True, to='pubbrain_app.BrainRegion', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='generation',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='level',
            field=models.PositiveIntegerField(default=None, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='lft',
            field=models.PositiveIntegerField(default=None, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='pubbrain_app.BrainRegion', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='rght',
            field=models.PositiveIntegerField(default=None, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='brainregion',
            name='tree_id',
            field=models.PositiveIntegerField(default=None, editable=False, db_index=True),
            preserve_default=False,
        ),
    ]
