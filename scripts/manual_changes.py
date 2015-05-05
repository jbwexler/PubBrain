"""
a method that performs manual changes to the BrainRegion objects.
"""

from pubbrain_app.models import BrainRegion, AtlasPkl
import os.path
import pubbrain_app
import PubBrain
from scripts import manual
from scripts.update_or_add_region import *


def tooBigList():
    pklDir = os.path.join(os.path.dirname(PubBrain), 'scripts/pickle_files/voxels')
    for object in AtlasPkl.objects.all():
        pass
        
        
# list of atlasRegions who have to many voxels and thus are not useful to map to through par/chi relations
tooBig = ['cerebral cortex']

def convertToList(filename):
    manualDir = manual.__path__[0]
    with open(os.path.join(manualDir, filename)) as fin:
        rows = [ line.split('\t') for line in fin ]
        d = { row[0]:row[1].replace('\n','') for row in rows[2:] }
    return d


def manualChanges():
    # keys are BrainRegion names and values are synonyms to be added
    
    pklDict = makePklDict()
    
    # keys are BrainRegion names and values are atlasregion names to be added
    atlasRegAdd = {}
    
    # list of names of BrainRegion objects to remove
    regionRem = ['white matter', 'matrix compartment', 'nucleus of cns']
    print 'regionRem: '
    for region in regionRem:
        try:
            object = BrainRegion.objects.get(name=region)
            object.delete()
        except Exception,e: print region, str(e)
        else:
            print 'removed: ', region
    print 
    # keys are BrainRegion names and values are children to Add
    
    print 'childAdd: '
    childAdd = convertToList('add_children.txt')
    for child, parent in childAdd.items():
        try:
            childObj = updateOrAddRegion(child, pklDict)
            parentObj = updateOrAddRegion(parent, pklDict)
            parentObj.allChildren.add(childObj)
            parentObj.save()
        except Exception,e: print child, parent, str(e)
        else:
            print 'added: %s as a child of: %s ' %(child, parent)
        
        
    # keys are BrainRegion names and values are children to remove
    print 'childRem:'
    childRem = convertToList('rem_children.txt')
    
    for region, child in childRem.items():
        try:
            object = BrainRegion.objects.get(name=region)
            childObj = BrainRegion.objects.get(name=child)
            object.allChildren.remove(childObj)
            object.save()
        except Exception,e: print region, str(e)
        else:
            print 'removed: %s - %s  parent-child relation' % (region, child)

# manualChanges()    
    
        
        