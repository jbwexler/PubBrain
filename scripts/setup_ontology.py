"""
script to set up toy example
"""


import django
import cPickle as pickle
import networkx as nx
from expand_syn import getSynonyms
import os
from nltk.sem.chat80 import region
django.setup()

from pubbrain_app import models

def setupOntology(graph):
    #takes a netx graph and adds each node. adds the following fields if applicable: synonyms, is_atlasregion, atlas_voxels, query, atlasregions
    with open(graph,'rb') as input:
        graph = pickle.load(input)
    
    for node in graph:
        name = graph.node[node]['name']
        synonymsInit = getSynonyms(name)
        
        #remove synonyms if they are only numbers
        synonyms = [syn for syn in synonymsInit if syn.isdigit() == False]
        
        # see if region or any synonyms are in atlas by seeing if their name matches pkl file.
        # if there's a match, the model object for each synonym should list that region as
        # atlasregions. the atlas region objects themselves should list the pkl file(s) as
        # atlas_voxels

        atlas_voxels = []
        for region in synonyms:
            formatName = region.replace('/', '_').replace(' ', '_') + '.pkl'
            for folder in os.listdir('pickle_files/voxels/'):
                if not folder.startswith('.'):
                    for file_name in os.listdir(os.path.join('pickle_files/voxels/', folder)):
                        if file_name == formatName:
                            atlas_voxels.append((os.path.join(folder, file_name)))
                        
    #     if atlas_voxels != {}:
    #         print synonyms, atlas_voxels
        
        # if region is new, will create it with query and is_atlasregion = False
        try:
            foo=models.BrainRegion.objects.get(name=name)
        except:
            foo=models.BrainRegion.create(name)
            foo.query='"' + region + '"[tiab]'
            foo.is_atlasregion=False
        if atlas_voxels:
            foo.is_atlasregion=True
        foo.save()
        # will then add/update atlas_voxels, synonyms and atlasregions
        if atlas_voxels:
            foo.atlasregions.add(foo)
            foo.atlas_voxels = ",".join(atlas_voxels)
        if synonyms:
            foo.synonyms = ",".join(synonyms)
        foo.save()
        # add parents
        parents = [graph.node[x]['name'] for x in graph.predecessors_iter(node)]
        for parent in parents:
            try:
                parentObj = models.BrainRegion.objects.get(name=parent)
            except:
                parentObj=models.BrainRegion.create(parent)
                parentObj.query='"' + region + '"[tiab]'
                parentObj.is_atlasregion=False
            parentObj.save()
            print parentObj.query
            foo.parents.add(parentObj)
            foo.save()
                
        #add children
        children = [graph.node[x]['name'] for x in graph.successors_iter(node)]
        for child in children:
            try:
                childObj = models.BrainRegion.objects.get(name=child)
            except:
                childObj=models.BrainRegion.create(child)
                childObj.query='"' + region + '"[tiab]'
                childObj.is_atlasregion=False
            childObj.save()
            childObj.parents.add(foo)
            childObj.save()
            
        
        
def parChiRecursion(region, direction, level = ''):
    level += '_'
    if region.is_atlasregion == True:
        print 'match'
        return [region]
    else:
        matchingRelatives = []
        if direction == 'parents':
            for parent in region.parents.all():
                print level, parent.name
                matchingRelatives += parChiRecursion(parent, direction, level)
        else:
            for child in region.children.all():
                print level, child.name
                matchingRelatives += parChiRecursion(child, direction, level)
        return matchingRelatives


def addParChiSearch():
    # for regions whose is_atlasregion == false, it will search through parents and children recursively to find regions that are atlas regions
    # and add these to the atlasregions field
    for region in models.BrainRegion.objects.filter(is_atlasregion=False):
        print region.name
        matches = parChiRecursion(region, 'parents') + parChiRecursion(region, 'children')
        for match in matches:
            region.atlasregions.add(match)
        

addParChiSearch()
    

# setupOntology("NIFgraph.pkl")

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
