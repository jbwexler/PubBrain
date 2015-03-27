from expand_syn import getSynonyms
from pubbrain_app.models import *

def compareNames(ontName, pklDict):
    # compares an ont region with all the pkl sets in the pklDict. returns a list of relative pkl paths of matching atlas regions
    ontName = filter(lambda x: str.isalnum(x) or str.isspace(x), ontName)
    ontRegSet = set(ontName.split(' '))
    voxels = []
    
    for name, words in pklDict.items():
        if words == ontRegSet:
            voxels.append(name)

    return voxels
   
def updateOrAddRegion(syn, pklDict):
    synonyms = getSynonyms(syn)
    
    # returns region if it or a synonym already exist. if region is new, will create it with query and is_atlasregion = False
    for syn in synonyms:
        fooList=BrainRegion.objects.filter(name=syn)
#         print fooList
        if fooList:
            foo = fooList[0]
            return foo
    else:
        'adding new'
        foo=BrainRegion.create(syn)
        foo.query='"' + syn + '"[tiab]'
        foo.is_atlasregion=False
        foo.save()
    
    # adds matching 
    atlas_voxels = []

    for region in synonyms:
        atlas_voxels += compareNames(region, pklDict) 


    # will then add/update atlasregions, atlas_voxels, is_atlasregion and synonyms
    if atlas_voxels:
        foo.atlasregions.add(foo)
        for atlasPklName in atlas_voxels:
            objectSet = AtlasPkl.objects.filter(name=atlasPklName)
            for object in objectSet:
                foo.atlas_voxels.add(object)
        foo.is_atlasregion=True
    if synonyms:
        foo.synonyms = "$".join(synonyms)
    foo.save()
    return foo

def makePklDict():
    pklList = [x.values()[0] for x in AtlasPkl.objects.all().values('name')]
    pklDict = {x:set(x.split(' ')) for x in pklList}
    return pklDict        