# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubbrain_app', '0005_auto_20150401_1046'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchToRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField(null=True, blank=True)),
                ('side', models.CharField(max_length=1, choices=[(b'l', b'left'), (b'r', b'right'), (b'u', b'uni')])),
                ('brain_region', models.ForeignKey(to='pubbrain_app.BrainRegion')),
                ('pubmed_search', models.ForeignKey(to='pubbrain_app.PubmedSearch')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='pubmedsearch',
            name='left_brain_regions',
        ),
        migrations.RemoveField(
            model_name='pubmedsearch',
            name='right_brain_regions',
        ),
        migrations.RemoveField(
            model_name='pubmedsearch',
            name='uni_brain_regions',
        ),
        migrations.AddField(
            model_name='pubmedsearch',
            name='brain_regions',
            field=models.ManyToManyField(to='pubbrain_app.BrainRegion', null=True, through='pubbrain_app.SearchToRegion', blank=True),
            preserve_default=True,
        ),
    ]
