from Bio import Entrez
from Bio.Entrez import efetch, read
import pickle
from pubbrain_app.models import BrainRegion, Pmid, PubmedSearch, SearchToRegion
from scipy.special._ufuncs import errprint
Entrez.email='poldrack@stanford.edu'
import datetime
import cProfile
import os
import django
from django.core.files import File
django.setup()
from pubbrain_app import models
from django.db import transaction
# from nipy.labs.viz import plot_map, mni_sform, coord_transform
import numpy as np
import nibabel as nib
import numpy.linalg as npl
from PubBrain.settings import BASE_DIR, MEDIA_ROOT

    


def arrayToText(data):
    with file('/Users/jbwexler/poldrack_lab/cs/other/array.txt', 'w') as outfile:
        outfile.write('# Array shape: {0}\n'.format(data.shape))
        for data_slice in data:
            np.savetxt(outfile, data_slice, fmt='%-7.2f')
            outfile.write('# New slice\n')

# def visualize(voxels):
#     mni_sform_inv = np.linalg.inv(mni_sform)
    

def pklsToNifti(searchObject, aff):
    
    sumArray = np.zeros((91,109,91))
    querySet = searchObject.searchtoregion_set.prefetch_related('brain_region').all()
    countDict = {}
    
    uniList = [x for x in querySet.filter(side='u').values_list('brain_region__mapped_regions__uni_pkls','count')]
    leftList = [x for x in querySet.filter(side='l').values_list('brain_region__mapped_regions__left_pkls','count')]
    rightList = [x for x in querySet.filter(side='r').values_list('brain_region__mapped_regions__right_pkls','count')]
    uniLeftList = [x for x in querySet.filter(side='ul').values_list('brain_region__mapped_regions__uni_pkls','count')] + [x for x in querySet.filter(side='ul').values_list('brain_region__mapped_regions__left_pkls', 'count')]
    uniRightList = [x for x in querySet.filter(side='ur').values_list('brain_region__mapped_regions__uni_pkls','count')] + [x for x in querySet.filter(side='ur').values_list('brain_region__mapped_regions__right_pkls', 'count')]
    
    allLists = uniList + leftList + rightList + uniLeftList + uniRightList
    for (pkl, count) in allLists:
        if pkl is not None and pkl != '':
            if countDict.get(pkl) == None:
                countDict[pkl] = int(count)
            else:
                countDict[pkl] += int(count)
        
    for pkl, count in countDict.items():
        print pkl, count
        with open(os.path.join(BASE_DIR,'scripts/pickle_files/atlas_region_voxels', pkl),'rb') as input:
            voxels = pickle.load(input)
        sumArray[voxels] += count
    print sumArray
    img = nib.Nifti1Image(sumArray, affine=aff)
    img.set_data_dtype(np.float32)
    return img

def tallyBrainRegions(idList, searchObject):
    # counts the number of instances each brain region in the results and adds these to the pubmed search object
    uniCount, leftCount, rightCount, uniLeftCount, uniRightCount = ({} for i in range(5))
    
    for id in idList:
        uniLeftBrainRegions = []
        uniRightBrainRegions = []
        try: uniBrainRegions = [x for x in id.uni_brain_regions.all()]
        except: uniBrainRegions = []
        try: leftBrainRegions = [x for x in id.left_brain_regions.all()]
        except: leftBrainRegions = []
        try: rightBrainRegions = [x for x in id.right_brain_regions.all()]
        except: rightBrainRegions = []
        
        for uni in uniBrainRegions:
            if uni in leftBrainRegions and uni in rightBrainRegions:
                leftBrainRegions.remove(uni)
                rightBrainRegions.remove(uni)
            elif uni in leftBrainRegions:
                uniBrainRegions.remove(uni)
                leftBrainRegions.remove(uni)
                uniLeftBrainRegions.append(uni)
            elif uni in rightBrainRegions:
                uniBrainRegions.remove(uni)
                rightBrainRegions.remove(uni)
                uniRightBrainRegions.append(uni)
                
        allLists = [[uniBrainRegions,uniCount], [leftBrainRegions,leftCount], [rightBrainRegions,rightCount], [uniLeftBrainRegions,uniLeftCount], [uniRightBrainRegions,uniRightCount]]

        for [l, d] in allLists:
            if l:
                for region in l:
                    if d.get(region) == None:
                        d[region] = 1
                    else:
                        d[region] += 1
    allDicts = {'u':uniCount, 'l':leftCount, 'r':leftCount, 'ul':uniLeftCount, 'ur':uniRightCount}
    for side, dict in allDicts.items():
        for region, count in dict.items():
            SearchToRegion.objects.create(brain_region=region, pubmed_search=searchObject, count=count, side=side)

            
def pubbrain_search(search):

    try:
        searchObject=PubmedSearch.objects.get(query=search)
    except:
        searchObject=PubmedSearch.create(search)
        searchObject.save()
        
    if searchObject.last_updated is None or (datetime.date.today() - searchObject.last_updated).days > 30:
        handle=Entrez.esearch(db='pubmed',term=search,retmax=100000)
        record = Entrez.read(handle)
        idList = Pmid.objects.filter(pubmed_id__in=record['IdList'])
        searchObject.pubmed_ids = idList
    #     data = np.arange(4*4*3).reshape(4,4,3)
    #     img = nib.Nifti1Image(data, affine=np.eye(4))
    #     nib.save(img, os.path.join('/Users/jbwexler/poldrack_lab/cs/other','test4d.nii.gz'))
        affine2mm = np.array([
            [-2, 0, 0, 90],
            [0, 2, 0, -126],
            [0, 0, 2, -72],
            [0, 0, 0, 1]])
    #     img = nib.load('/Applications/fmri_progs/fsl/data/atlases/STN/STN-maxprob-thr25-0.5mm.nii.gz')
    #     data = img.get_data()
        
        tallyBrainRegions(idList, searchObject)
        
        
        img = pklsToNifti(searchObject, affine2mm)
        filename = os.path.join(MEDIA_ROOT, 'temp', search +'.nii.gz')
        nib.save(img, filename)
        with open(filename) as imgFile:
            searchObject.file = File(imgFile)
            searchObject.last_updated = datetime.date.today()
            searchObject.save()
        os.remove(filename)
        
    return searchObject
    

        
 
cProfile.runctx("pubbrain_search('vision')", None, locals())
