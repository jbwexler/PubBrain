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
import profile
from PubBrain.settings import BASE_DIR
import numpy as np
django.setup()

from pubbrain_app import models


def setupOntology(pkl):
    #takes a netx graph and adds each node. adds the following fields if applicable: synonyms, is_atlasregion, atlas_regions, query, mapped_regions
    with open(pkl,'rb') as inputFile:
        graph = pickle.load(inputFile)
    
    pklDict = makePklDict()

    for node in graph:
        if 'name' not in graph.node[node].keys():
            continue
        regionNameFull = graph.node[node]['name']
        #remove left and right
        regionName = regionNameFull.replace('right ', '').replace('left ', '')

        parents = [graph.node[x]['name'] for x in graph.predecessors_iter(node) if 'name' in graph.node[x].keys()]
        children = [graph.node[x]['name'] for x in graph.successors_iter(node) if 'name' in graph.node[x].keys()]
        if not parents and not children:
            continue
        
        foo = updateOrAddRegion(regionName, pklDict, pkl)
        # add allParents
        # should be able to remove the if part of next line (and children) once i fix the graph
        
        for parentFull in parents:
            parent = parentFull.replace('right ', '').replace('left ', '')
            if parent != regionName:
                parentObj = updateOrAddRegion(parent, pklDict, pkl)
                foo.allParents.add(parentObj)
                foo.save()
                
        #add children
        for childFull in children:
            child = childFull.replace('right ', '').replace('left ', '')
            if child != regionName:
                childObj = updateOrAddRegion(child, pklDict, pkl)
                childObj.allParents.add(foo)
                childObj.save()
        
def combinePkls(pkls):        
    atlas_mask = np.zeros((91,109,91))
    for pkl in pkls:
        with open(os.path.join(BASE_DIR,'scripts/pickle_files/atlas_region_voxels', pkl),'rb') as input:
            voxArray = pickle.load(input)
        atlas_mask[voxArray] = True
    return np.where(atlas_mask)
    
    
def addAllPkls():
    # for each brainregion that has is mapped to AtlasPkl(s), will add the appropriate pkl files to the brainregion
    # if there are multiple AtlasPkls, it will combine them into new pkl files saved in the 'atlas_region_voxels/ontology
    for region in BrainRegion.objects.filter(atlas_regions__isnull=False):
        uniPkls = [x for (x,) in region.atlas_regions.all().values_list('uni_pkl') if x is not None]
        leftPkls = [x for (x,) in region.atlas_regions.all().values_list('left_pkl') if x is not None]
        rightPkls = [x for (x,) in region.atlas_regions.all().values_list('right_pkl') if x is not None]
        pklDir = os.path.join(BASE_DIR,'scripts/pickle_files/atlas_region_voxels' )
        
        
        if len(uniPkls) > 1:
            uniArray = combinePkls(uniPkls)
            pklFile = region.name.replace('/', '_').replace(' ', '_') + '.pkl'
            uni = os.path.join('ontology', pklFile)
            with open(os.path.join(pklDir, uni),'wb') as output:
                pickle.dump(uniArray, output, -1)
        elif len(uniPkls) == 1:
            uni = uniPkls[0]
        else:
            uni = ''
            
        if len(leftPkls) > 1:
            leftArray = combinePkls(leftPkls)
            pklFile = region.name.replace('/', '_').replace(' ', '_') + '.pkl'
            left = os.path.join('ontology', pklFile)
            with open(os.path.join(pklDir, left),'wb') as output:
                pickle.dump(leftArray, output, -1)
        elif len(leftPkls) == 1:
            left = leftPkls[0]
        else:
            left = ''
            
        if len(rightPkls) > 1:
            rightArray = combinePkls(rightPkls)
            pklFile = region.name.replace('/', '_').replace(' ', '_') + '.pkl'
            right = os.path.join('ontology', pklFile)
            with open(os.path.join(pklDir, right),'wb') as output:
                pickle.dump(rightArray, output, -1)
        elif len(rightPkls) == 1:
            right = rightPkls[0]
        else:
            right = ''
            
        region.uni_pkls = uni
        region.left_pkls = left
        region.right_pkls = right
        region.save()
 
def parChiRecursion(region, direction, level = ''):
    level += '_'
    if region.has_pkl == True and region.name not in tooBig:
        print '!!!!match!!!!'
        return [region]
    else:
        matchingRelatives = []
        if direction == 'parents':
            for parent in region.parent.all():
                print level, len(level), parent.name
                matchingRelatives += parChiRecursion(parent, direction, level)
        else:
            for child in region.children.all():
                print level, len(level), child.name
                matchingRelatives += parChiRecursion(child, direction, level)
        return matchingRelatives


def addParChiSearch():
    # for regions whose has_pkl == false, it will search through parents and children recursively to find regions that are atlas regions
    # and add these to the mapped_regions field
    for region in models.BrainRegion.objects.filter(has_pkl=False):
        print region.name
        matches = parChiRecursion(region, 'parents') + parChiRecursion(region, 'children')
        region.mapped_regions.clear()
        region.save()
        for match in matches:
            region.mapped_regions.add(match)

def addAtlasPkls():
    # adds an AtlasPkl object for each .pkl file in the voxels dir
    for folder in os.listdir('pickle_files/atlas_region_pickles/'):
        if not folder.startswith('.'):
            for fileName in os.listdir(os.path.join('pickle_files/atlas_region_voxels/', folder)):
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
               
def delSamePar():
    #removes self-parent and self-child relationships
    for region in BrainRegion.objects.all():
        if region in region.allParents.all():
            region.allParents.remove(region)
            region.save()
        if region in region.allChildren.all():
            region.allChildren.remove(region)
            region.save()
                
def redoSyns():
    # will update the synonyms of each BrainRegion
    # warning!!! doesn't include manually added synonyms. maybe add this in future?
    for region in BrainRegion.objects.exclude(synonyms=None):
        newSyn = getSynonyms(region.name)
        newSynStr = "$".join(newSyn)
        print newSynStr
        region.synonyms = newSynStr
        region.save()

def updateAtlasMappings():
    pklDict = makePklDict()
    for region in BrainRegion.objects.all():
        synonyms = region.synonyms.split('$')
        print region
        atlas_regions = []
        for syn in synonyms:
            atlas_regions += compareNames(str(syn), pklDict) 
        
        if atlas_regions:
            region.mapped_regions.add(region)
            for atlasPklName in atlas_regions:
                objectSet = AtlasPkl.objects.filter(name=atlasPklName)
                for object in objectSet:
                    region.atlas_regions.add(object)
            region.has_pkl=True
        region.save()

def updateAtlasMappings():
    pklDict = makePklDict()
    for region in BrainRegion.objects.all():
        synonyms = region.synonyms.split('$')
        print region
        atlas_voxels = []
        for syn in synonyms:
            atlas_voxels += compareNames(str(syn), pklDict) 
        
        if atlas_regions:
            region.mapped_regions.add(region)
            for atlasPklName in atlas_regions:
                objectSet = AtlasPkl.objects.filter(name=atlasPklName)
                for object in objectSet:
                    region.atlas_regions.add(object)
            region.has_pkl=True
        region.save()
        

def delSynRegions():
    for region in BrainRegion.objects.all():
        querySet = BrainRegion.objects.filter(name=region.name)
        if querySet.count() > 1:
            pk = [x.pk for x in querySet]
            pmids = [x.sumPmids() for x in querySet]
            maxIndex = pmids.index(max(pmids))
            dontDelete = pk[maxIndex]
            print dontDelete
#             querySet.exclude(pk=dontDelete).delete()
            for x in querySet.all():
                print x.name, x.pk, x.sumPmids()
            
        
def bestParent():
    # chooses a best parent from 'allParents' and adds it to 'parent'
    # best parent is determined by the one that is not a parent
    pass
    
def freshStart():
    #performs all steps necessary to setup ontology when creating a fresh database. the order of the ontology graphs is important
    #to keep the BrainRegion names the same as before
    addAtlasPkls()
    setupOntology("NIFgraph.pkl")
    setupOntology("uberongraph.pkl")
    setupOntology("FMAgraph.pkl")
    manualChanges()
    delSynRegions()
    delSamePar()
    addParChiSearch()
    addAllPkls()

# freshStart()
# addAtlasPkls()
# manualChanges()
# returnLoopRegions()
# delSynRegions()
# delSamePar()
# printSynRegions()
# addParChiSearch()
# updateAtlasMappings()
# addAllPkls()
# setupOntology("NIFgraph.pkl")
# setupOntology("uberongraph.pkl")
# setupOntology("FMAgraph.pkl")
# manualChanges()
# delSamePar()
delSynRegions()