# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AtlasPkl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(max_length=1000)),
                ('atlas', models.TextField(max_length=1000, null=True, blank=True)),
                ('pkl', models.TextField(max_length=1000, null=True, blank=True)),
                ('side', models.TextField(blank=True, max_length=1000, null=True, choices=[(b'left', b'left'), (b'right', b'right'), (b'unilateral', b'unilateral')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrainRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(max_length=1000)),
                ('query', models.CharField(max_length=255)),
                ('is_atlasregion', models.BooleanField(default=False)),
                ('synonyms', models.TextField(null=True, blank=True)),
                ('last_indexed', models.DateField(null=True, blank=True)),
                ('left_atlas_regions', models.ManyToManyField(related_name='left_brainregions', null=True, to='pubbrain_app.BrainRegion', blank=True)),
                ('left_atlas_voxels', models.ManyToManyField(related_name='left_brainregions', to='pubbrain_app.AtlasPkl')),
                ('parents', models.ManyToManyField(related_name='children', null=True, to='pubbrain_app.BrainRegion', blank=True)),
                ('right_atlas_regions', models.ManyToManyField(related_name='right_brainregions', null=True, to='pubbrain_app.BrainRegion', blank=True)),
                ('right_atlas_voxels', models.ManyToManyField(related_name='right_brainregions', to='pubbrain_app.AtlasPkl')),
                ('uni_atlas_regions', models.ManyToManyField(related_name='uni_brainregions', null=True, to='pubbrain_app.BrainRegion', blank=True)),
                ('uni_atlas_voxels', models.ManyToManyField(related_name='uni_brainregions', to='pubbrain_app.AtlasPkl')),
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
