# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BrainRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('query', models.CharField(max_length=255)),
                ('is_atlasregion', models.BooleanField(default=False)),
                ('atlas_voxels', models.TextField()),
                ('last_indexed', models.DateField(auto_now=True, auto_now_add=True)),
                ('atlasregions', models.ManyToManyField(related_name='+', null=True, to='pubbrain_app.BrainRegion', blank=True)),
                ('children', models.ManyToManyField(related_name='children_rel_+', null=True, to='pubbrain_app.BrainRegion', blank=True)),
                ('parent', models.ForeignKey(blank=True, to='pubbrain_app.BrainRegion', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pmid',
            fields=[
                ('pubmed_id', models.IntegerField(max_length=20, serialize=False, primary_key=True, db_index=True)),
                ('date_added', models.DateField(auto_now=True, auto_now_add=True)),
                ('title', models.CharField(default=b'', max_length=255)),
                ('brain_regions_named', models.ManyToManyField(to='pubbrain_app.BrainRegion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PubmedSearch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateField(auto_now=True, auto_now_add=True)),
                ('filename', models.CharField(max_length=255)),
                ('date_file_saved', models.DateField(auto_now=True, auto_now_add=True)),
                ('query', models.CharField(max_length=255)),
                ('pubmed_ids', models.ManyToManyField(to='pubbrain_app.Pmid')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
