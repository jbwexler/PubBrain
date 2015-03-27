"""
script to set up ontology
"""


import django
import cPickle as pickle
from scripts.expand_syn import getSynonyms
import os
from nltk.sem.chat80 import region
from pip._vendor.distlib._backport.tarfile import TUREAD
from scripts.manual_changes import manualChanges, tooBig
from pubbrain_app.models import *
import scripts.manual_changes
from scripts.update_or_add_region import *
django.setup()

from pubbrain_app import models


def setupOntology(pkl):
    #takes a netx graph and adds each node. adds the following fields if applicable: synonyms, is_atlasregion, atlas_voxels, query, atlasregions
    with open(pkl,'rb') as inputFile:
        graph = pickle.load(inputFile)
    
    pklDict = makePklDict()

    for node in graph:
        if 'name' not in graph.node[node].keys():
            continue
        syn = graph.node[node]['name']
        #remove left and right
        syn = syn.replace('right ', '').replace('left ', '')

        parents = [graph.node[x]['name'] for x in graph.predecessors_iter(node) if 'name' in graph.node[x].keys()]
        children = [graph.node[x]['name'] for x in graph.successors_iter(node) if 'name' in graph.node[x].keys()]
        if not parents and not children:
            continue
        
        foo = updateOrAddRegion(syn, pklDict)
        # add parents
        # should be able to remove the if part of next line (and children) once i fix the graph
        
        for parent in parents:
            parent = parent.replace('right ', '').replace('left ', '')
            if parent != syn:
                parentObj = updateOrAddRegion(parent, pklDict)
                foo.parents.add(parentObj)
                foo.save()
                
        #add children
        for child in children:
            child = child.replace('right ', '').replace('left ', '')
            if child != syn:
                childObj = updateOrAddRegion(child, pklDict)
                childObj.parents.add(foo)
                childObj.save()
        
        
def parChiRecursion(region, direction, level = ''):
    level += '_'
    if region.is_atlasregion == True and region.name not in tooBig:
        print '!!!!match!!!!'
        return [region]
    else:
        matchingRelatives = []
        if direction == 'parents':
            for parent in region.parents.all():
                print level, len(level), parent.name
                matchingRelatives += parChiRecursion(parent, direction, level)
        else:
            for child in region.children.all():
                print level, len(level), child.name
                matchingRelatives += parChiRecursion(child, direction, level)
        return matchingRelatives


def addParChiSearch():
    # for regions whose is_atlasregion == false, it will search through parents and children recursively to find regions that are atlas regions
    # and add these to the atlasregions field
    for region in models.BrainRegion.objects.filter(is_atlasregion=False):
        print region.name
        matches = parChiRecursion(region, 'parents') + parChiRecursion(region, 'children')
        region.atlasregions.clear()
        region.save()
        for match in matches:
            region.atlasregions.add(match)

def addAtlasPkls():
    # adds an AtlasPkl object for each .pkl file in the voxels dir
    for folder in os.listdir('pickle_files/voxels/'):
        if not folder.startswith('.'):
            for fileName in os.listdir(os.path.join('pickle_files/voxels/', folder)):
                pkl = os.path.join(folder,fileName)
                atlas = folder.replace('_', ' ')
                
                #clean up the name
                actualName = fileName.replace('_', ' ').replace('.pkl', '')
                actualSplit = actualName.split(' ')
                removeList = ['wm', 'gm', 'division', 'l', 'r', 'right', 'left']
                split = [x for x in actualSplit if x not in removeList]
                name = ' '.join(split)
                name = filter(lambda x: str.isalnum(x) or str.isspace(x), name)
                
                print pkl, atlas, name
                try:
                    foo = AtlasPkl.objects.get(name=name, atlas=atlas)
                    print 'using exist'
                except:
                    foo = AtlasPkl.create(name)
                    print 'creating new'
                foo.atlas = atlas
                
                if 'l' in actualSplit or 'left' in actualSplit:
                    foo.left_pkl = pkl
                elif 'r' in actualSplit or 'right' in actualSplit:
                    foo.right_pkl = pkl
                else:
                    foo.uni_pkl = pkl
                foo.save()

def printSynRegions():
    # prints regions that are duplicates or whose synonyms already exist
    
    for region in BrainRegion.objects.exclude(synonyms=None):
        synonyms = region.synonyms.split("$")
        synonyms.remove(region.name)
        for syn in synonyms:
            fil = BrainRegion.objects.filter(name=syn)
            if fil:
                print [x.name for x in fil]
    
    for region in BrainRegion.objects.all():
        fil = BrainRegion.objects.filter(name=region.name)
        if len(fil) > 1:
            print [x.name for x in fil]
    
# def delSynRegions():
#     # deletes regions that who are a synonym of another region (presumably only an issue w/ multiple ontologies). note: the updated setupOntology()
#     # function will prevent synonym regions from being created so this function won't be necessary for now on
#     # update: 
#     for region in BrainRegion.objects.exclude(synonyms=None):
#         synonyms = region.synonyms.split("$")
#         synonyms.remove(region.name)
#         for syn in synonyms:
#             if BrainRegion.objects.filter(name=syn):
#                 region.delete()
#                 region.save()
#                 print syn
#                 print "deleted: %s" %region.name
                
def delSamePar():
    #removes self-parent and self-child relationships
    for region in BrainRegion.objects.all():
        if region in region.parents.all():
            region.parents.remove(region)
            region.save()
        if region in region.children.all():
            region.children.remove(region)
            region.save()

def redoSyns():
    # will update the synonyms of each BrainRegion
    for region in BrainRegion.objects.exclude(synonyms=None):
        newSyn = getSynonyms(region.name)
        newSynStr = "$".join(newSyn)
        print newSynStr
        region.synonyms = newSynStr
        region.save()

def returnLoopRegions():
    #prints regions who has a region that is both a parent and a child. this will cause recursive loop when running addParChiSearch()
    for region in [x for x in BrainRegion.objects.all() if x.parents.all() and x.children.all()]:
#         print set(x.parents.all()).intersection(x.children.all())
#         print x.parents.all()
#         print x.children.all()
        loopRegions = []
        if set(region.parents.all()).intersection(region.children.all()):
            loopRegions.append(region)
            print region.name
        return loopRegions

def updateAtlasMappings():
    pklDict = makePklDict()
    for region in BrainRegion.objects.all():
        synonyms = region.synonyms.split('$')
        print region
        atlas_voxels = []
        for syn in synonyms:
            atlas_voxels += compareNames(str(syn), pklDict) 
        
        if atlas_voxels:
            region.atlasregions.add(region)
            for atlasPklName in atlas_voxels:
                objectSet = AtlasPkl.objects.filter(name=atlasPklName)
                for object in objectSet:
                    region.atlas_voxels.add(object)
            region.is_atlasregion=True
        region.save()
        

def freshStart():
    #performs all steps necessary to setup ontology when creating a fresh database. the order of the ontology graphs is important
    #to keep the BrainRegion names the same as before
    addAtlasPkls()
    setupOntology("NIFgraph.pkl")
    setupOntology("uberongraph.pkl")
    setupOntology("FMAgraph.pkl")
    manualChanges()
    delSamePar()
    addParChiSearch()
    
# freshStart()
# addAtlasPkls()
# manualChanges()
# returnLoopRegions()
# delSynRegions()
# delSamePar()
# printSynRegions()
addParChiSearch()
# updateAtlasMappings()

