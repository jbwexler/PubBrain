"""
script to set up ontology
"""


import django
import cPickle as pickle
from scripts.expand_syn import getSynonyms
import os
from nltk.sem.chat80 import region
from pip._vendor.distlib._backport.tarfile import TUREAD
from scripts.manual_changes import *
from pubbrain_app.models import *
import scripts.manual_changes
django.setup()

from pubbrain_app import models

def compareNames(ontName, pklDict):
    # compares an ont region with all the pkl sets in the pklDict. returns a list of relative pkl paths of matching atlas regions
    ontName = filter(lambda x: str.isalnum(x) or str.isspace(x), ontName)
    ontRegSet = set(ontName.split(' '))
    voxels = []
    
    for object, words in pklDict.items():
        if words == ontRegSet:
            voxels.append(object)

    return voxels

def decodeVoxelPkls():
    # creates a dictionary with keys as relative pkl paths and values as sets of words corresponding to the region name
    pklDict = {}
    removeSet = set(['wm', 'gm', 'division', 'l', 'r', 'right', 'left'])
    for object in AtlasPkl.objects.all():
        atlasReg = str(object.name)
        atlasReg = filter(lambda x: str.isalnum(x) or str.isspace(x), atlasReg)
        atlasRegSet = set(atlasReg.split(' '))
        atlasRegSet.difference_update(removeSet)
        pklDict[object] = atlasRegSet
    return pklDict     
                
def updateOrAddRegion(regionName, pklDict):
    synonyms = getSynonyms(regionName)
    
    # returns region if it or a synonym already exist. if region is new, will create it with query and is_atlasregion = False
    for syn in synonyms:
        fooList=models.BrainRegion.objects.filter(name=syn)
#         print fooList
        if fooList:
            foo = fooList[0]
            break
    else:
        'adding new'
        foo=models.BrainRegion.create(regionName)
        foo.query='"' + regionName + '"[tiab]'
        foo.is_atlasregion=False
        foo.save()
    
    # adds matching 
    atlas_voxels = []

    for region in synonyms:
        atlas_voxels += compareNames(region, pklDict) 


    # will then add/update atlasregions, atlas_voxels, is_atlasregion and synonyms
    if atlas_voxels:
        foo.atlasregions.add(foo)
        for object in atlas_voxels:
            if object.side == 'left':
                foo.left_atlas_voxels.add(object)
            elif object.side == 'right':
                foo.right_atlas_voxels.add(object)
            else:
                foo.uni_atlas_voxels.add(object)
        foo.is_atlasregion=True
    if synonyms:
        foo.synonyms = "$".join(synonyms)
    foo.save()
    return foo
                
def setupOntology(pkl):
    #takes a netx graph and adds each node. adds the following fields if applicable: synonyms, is_atlasregion, atlas_voxels, query, atlasregions
    with open(pkl,'rb') as inputFile:
        graph = pickle.load(inputFile)
    
    pklDict = decodeVoxelPkls()
    for node in graph:
        if 'name' not in graph.node[node].keys():
            continue
        regionName = graph.node[node]['name']
        #remove left and right
        regionName = regionName.replace('right ', '').replace('left ', '')

        parents = [graph.node[x]['name'] for x in graph.predecessors_iter(node) if 'name' in graph.node[x].keys()]
        children = [graph.node[x]['name'] for x in graph.successors_iter(node) if 'name' in graph.node[x].keys()]
        if not parents and not children:
            print regionName
            continue
        
        foo = updateOrAddRegion(regionName, pklDict)
        # add parents
        # should be able to remove the if part of next line (and children) once i fix the graph
        
        for parent in parents:
            parent = parent.replace('right ', '').replace('left ', '')
            if parent != regionName:
                parentObj = updateOrAddRegion(parent, pklDict)
                foo.parents.add(parentObj)
                foo.save()
                
        #add children
        for child in children:
            child = child.replace('right ', '').replace('left ', '')
            if child != regionName:
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
                name = fileName.replace('_', ' ').replace('.pkl', '')
                print pkl, atlas, name
                try:
                    AtlasPkl.objects.get(pkl=pkl)
                except:
                    foo = AtlasPkl.create(pkl)
                foo.atlas = atlas
                foo.name = name
                split = name.split(' ')
                if 'l' in split or 'left' in split:
                    foo.side = 'left'
                elif 'r' in split or 'right' in split:
                    foo.side = 'right'
                else:
                    foo.side = 'unilateral'
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
    
def delSynRegions():
    # deletes regions that who are a synonym of another region (presumably only an issue w/ multiple ontologies). note: the updated setupOntology()
    # function will prevent synonym regions from being created so this function won't be necessary for now on
    for region in BrainRegion.objects.exclude(synonyms=None):
        synonyms = region.synonyms.split("$")
        synonyms.remove(region.name)
        for syn in synonyms:
            if BrainRegion.objects.filter(name=syn):
                region.delete()
                region.save()
                print syn
                print "deleted: %s" %region.name
                
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
        

def freshStart():
    #performs all steps necessary to setup ontology when creating a fresh databse
    addAtlasPkls()
    setupOntology("NIFgraph.pkl")
    setupOntology("uberongraph.pkl")
    setupOntology("FMAgraph.pkl")
    manualChanges()
    delSynRegions()
    delSamePar()
    addParChiSearch()
    
# freshStart()
# manualChanges()
# returnLoopRegions()
# delSynRegions()
# delSamePar()
# printSynRegions()
addParChiSearch()


