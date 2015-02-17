"""
script to set up toy example
"""


import django
import cPickle as pickle
import networkx as nx
from pubbrain_app.scripts.expand_syn import getSynonyms
import os
django.setup()

from pubbrain_app import models

def setupOntology():
    with open('NIFgraph.pkl','rb') as input:
        nif = pickle.load(input)
    
    for node in nif:
        name = nif.node[node]['name']
        synonyms = getSynonyms(name)
    
        # see if region or any synonyms are in atlas by seeing if their name matches pkl file.
        # if there's a match, the model object for each synonym should list that region as
        # atlasregions. the atlas region objects themselves should list the pkl file(s) as
        # atlas_voxels
        
        atlas_voxels = {}
        for region in synonyms:
            formatName = region.replace('/', '_').replace(' ', '_') + '.pkl'
            for folder in os.listdir('pickle_files/voxels/'):
                if not folder.startswith('.'):
                    for file_name in os.listdir(os.path.join('pickle_files/voxels/', folder)):
                        if file_name == formatName:
                            atlas_voxels[region] = (os.path.join(folder, file_name))
                        
    #     if atlas_voxels != {}:
    #         print synonyms, atlas_voxels
        
        for region in synonyms:
            #make sure region isn't just a digit. some synonyms are just digits
            if not region.isdigit():
                try:
                    foo=models.BrainRegion.objects.get(name=region)
                except:
                    foo=models.BrainRegion.create(region)
                    foo.query='"' + region + '"[tiab]'
                    foo.is_atlasregion=False
                if atlas_voxels != {}:
                    for key in atlas_voxels.keys():
                        foo.atlasregions.add(models.BrainRegion.objects.get(name=key))
                    if region in atlas_voxels.keys():
                        foo.is_atlasregion = True
                        foo.atlas_voxels = atlas_voxels[region]
                foo.save()

setupOntology()

#execfile('scripts/index_pubmed.py')

# use the outputs from mk_combined_atlas.py
# generate a toy atlas dictionary
# f=open('scripts/atlas_to_ontology_dict.txt','w')
# f.write('hippocampus\thippocampus\n')
# f.write('inferior frontal gyrus\tinferior frontal gyrus\n')
# f.write('middle frontal gyrus\tmiddle frontal gyrus\n')
# f.close()
# 
# 
# # use the toy dictionary to add voxel mappings for atlas regions to db
# #execfile('scripts/link_atlasRegions_to_brainRegions.py')
# 
# srch=models.PubmedSearch.create('hippocampus')
# srch.save()
# srch.pubmed_ids.add(models.Pmid.objects.get(pubmed_id='25244639'))
# srch.pubmed_ids.add(models.Pmid.objects.get(pubmed_id='25244085'))
# srch.pubmed_ids.add(models.Pmid.objects.get(pubmed_id='14497900'))
# srch.pubmed_ids.add(models.Pmid.objects.get(pubmed_id='22511924'))
