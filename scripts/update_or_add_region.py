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


   
def updateOrAddRegion(regionName, pklDict, pkl=''):
    synonyms = getSynonyms(regionName)
    
    # returns region if it or a synonym already exist. if region is new, will create it with query and is_atlasregion = False
    for syn in synonyms:
        fooList=BrainRegion.objects.filter(name=syn)
#         print fooList
        if fooList:
            foo = fooList[0]
            break
#             return foo
    else:
        'adding new'
        foo=BrainRegion.create(regionName)
        foo.query='"' + regionName + '"[tiab]'
        foo.has_pkl=False
        foo.save()
    
    
    print pkl, regionName
    if pkl == 'NIFgraph.pkl':
        foo.NIF_name = regionName
    elif pkl == 'uberongraph.pkl':
        foo.Uberon_name = regionName
    elif pkl == 'FMAgraph.pkl':
        foo.FMA_name = regionName
    
    
    # adds matching 
    atlas_regions = []

    for region in synonyms:
        atlas_regions += compareNames(region, pklDict) 


    # will then add/update mapped_regions, atlas_regions, has_pkl and synonyms
    if atlas_regions:
        foo.mapped_regions.add(foo)
        for atlasPklName in atlas_regions:
            objectSet = AtlasPkl.objects.filter(name=atlasPklName)
            for object in objectSet:
                foo.atlas_regions.add(object)
        foo.has_pkl=True
    if synonyms:
        foo.synonyms = "$".join(synonyms)
    foo.save()
    return foo


def makePklDict():
    pklList = [x.values()[0] for x in AtlasPkl.objects.all().values('name')]
    pklDict = {x:set(x.split(' ')) for x in pklList}
    return pklDict        