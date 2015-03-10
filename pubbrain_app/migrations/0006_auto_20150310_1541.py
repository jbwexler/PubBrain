# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0005_auto_20150220_1359'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtlasPkl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(max_length=1000)),
                ('atlas', models.TextField(max_length=1000)),
                ('pkl', models.TextField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='brainregion',
            name='atlas_voxels1',
            field=models.ManyToManyField(related_name='BrainRegions', to='pubbrain_app.AtlasPkl'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='brainregion',
            name='last_indexed',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
