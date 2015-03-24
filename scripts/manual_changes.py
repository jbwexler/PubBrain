"""
a method that performs manual changes to the BrainRegion objects.
"""

from pubbrain_app.models import BrainRegion, AtlasPkl
import os.path
import pubbrain_app
import PubBrain

def tooBigList():
    pklDir = os.path.join(os.path.dirname(PubBrain), 'scripts/pickle_files/voxels')
    for object in AtlasPkl.objects.all():
        pass
        
        
# list of atlasRegions who have to many voxels and thus are not useful to map to through par/chi relations
tooBig = ['cerebral cortex']

def manualChanges():
    # keys are BrainRegion names and values are synonyms to be added
    synAdd = {}
    print 'synAdd:'
    for region, syn in synAdd.items():
        try:
            object = BrainRegion.objects.get(name=region)
            synonyms = object.synonyms.split('$')
            synonyms.append(syn)
            object.synonyms = "$".join(synonyms)
            object.save()
        except Exception,e: print region, str(e)
        else:
            print 'added:, ', region, syn
    print
    # keys are BrainRegion names and values are synonyms to be removed
    synRem = {'dorsal supraoptic decussation':'dorsal', 'ventral supraoptic decussation':'ventral', 'ca2 field of hippocampus':'ca2'}
    print 'synRemo: '
    for region, syn in synRem.items():
        try:
            object = BrainRegion.objects.get(name=region)
            synonyms = object.synonyms.split('$')
            synonyms.remove(syn)
            object.synonyms = "$".join(synonyms)
            object.save()
        except Exception,e: print region, str(e)
        else:
            print 'removed: ', region, syn
    print  
    # keys are BrainRegion names and values are atlasregion names to be added
    atlasRegAdd = {}
    
    # list of names of BrainRegion objects to remove
    regionRem = ['brain', 'white matter', 'matrix compartment', 'nucleus of cns' ]
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
    childAdd = {}
    
    for region, child in childAdd.items():
        try:
            object = BrainRegion.objects.get(name=region)
            childObj = BrainRegion.objects.get(name=child)
            object.children.add(childObj)
            object.save()
        except Exception,e: print region, str(e)
        
        
    # keys are BrainRegion names and values are children to remove
    print 'childRem:'
    childRem = {'olfactory bulb': 'olfactory lobe', 'core auditory cortex':'auditory cortex','cerebral hemisphere':'cerebral cortex','body of hippocampus':'hippocampus'}
    for region, child in childRem.items():
        try:
            object = BrainRegion.objects.get(name=region)
            childObj = BrainRegion.objects.get(name=child)
            object.children.remove(childObj)
            object.save()
        except Exception,e: print region, str(e)
        else:
            print 'removed: %s - %s  parent-child relation' % (region, child)
    
    # keys are BrainRegion names and values are parents to Add
    parentAdd = {}
    for region, parent in parentAdd.items():
        try:
            object = BrainRegion.objects.get(name=region)
            parentObj = BrainRegion.objects.get(name=parent)
            object.parents.add(parentObj)
            object.save()
        except Exception,e: print region, str(e)
    
    # keys are BrainRegion names and values are parents to remove
    parentRem = {}
    for region, parent in parentRem.items():
        try:
            object = BrainRegion.objects.get(name=region)
            parentObj = BrainRegion.objects.get(name=parent)
            object.parents.remove(parentObj)
            object.save()
        except Exception,e: print region, str(e)
        
    
        
        