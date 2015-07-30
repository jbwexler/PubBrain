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
from collections import Counter
from django.db.models import Count
from PubBrain.settings import BASE_DIR, MEDIA_ROOT
from django.db.models import Q


    


def arrayToText(data):
    with file('/Users/jbwexler/poldrack_lab/cs/other/array.txt', 'w') as outfile:
        outfile.write('# Array shape: {0}\n'.format(data.shape))
        for data_slice in data:
            np.savetxt(outfile, data_slice, fmt='%-7.2f')
            outfile.write('# New slice\n')

# def visualize(voxels):
#     mni_sform_inv = np.linalg.inv(mni_sform)
    

def pklsToNifti(searchObject, aff):
    time1 = datetime.datetime.now()
    sumArray = np.zeros((91,109,91))
    querySet = searchObject.searchtoregion_set.prefetch_related('brain_region').all()
    countDict = {}
    
    uniList = [x for x in querySet.filter(side='u').values_list('brain_region__mapped_regions__uni_pkls','count')]
    leftList = [x for x in querySet.filter(side='l').values_list('brain_region__mapped_regions__left_pkls','count')]
    rightList = [x for x in querySet.filter(side='r').values_list('brain_region__mapped_regions__right_pkls','count')]
    uniLeftList = [x for x in querySet.filter(side='ul').values_list('brain_region__mapped_regions__uni_pkls','count')] + [x for x in querySet.filter(side='ul').values_list('brain_region__mapped_regions__left_pkls', 'count')]
    uniRightList = [x for x in querySet.filter(side='ur').values_list('brain_region__mapped_regions__uni_pkls','count')] + [x for x in querySet.filter(side='ur').values_list('brain_region__mapped_regions__right_pkls', 'count')]
    
    time2 = datetime.datetime.now()
    
    allLists = uniList + leftList + rightList + uniLeftList + uniRightList
    for (pkl, count) in allLists:
        if pkl and 'cerebral_cortex' not in pkl:
            if countDict.get(pkl) == None:
                countDict[pkl] = int(count)
            else:
                countDict[pkl] += int(count)
        
    for pkl, count in countDict.items():
        with open(os.path.join(BASE_DIR,'scripts/pickle_files/atlas_region_voxels', pkl),'rb') as input:
            voxels = pickle.load(input)
        sumArray[voxels] += count
    img = nib.Nifti1Image(sumArray, affine=aff)
    img.set_data_dtype(np.float32)
    
    time3 = datetime.datetime.now()
    print time2 - time1
    print time3 - time2
    print
    
    return img

def tallyBrainRegions(idList, searchObject):
    # counts the number of instances each brain region in the results and adds these to the pubmed search object
    time1 = datetime.datetime.now()
#     uniList = BrainRegion.objects.filter(uni_pmids__in=idList)
#     print uniList.query
#     uniList = list(uniList)
#     leftList = list(BrainRegion.objects.filter(left_pmids__in=idList))
#     rightList = list(BrainRegion.objects.filter(right_pmids__in=idList))
#     uniLeftList = []
#     uniRightList = []
    
    uniCount = list(idList.values_list('uni_brain_regions').annotate(the_count=Count('uni_brain_regions')))
    leftCount = list(idList.values_list('left_brain_regions').annotate(the_count=Count('left_brain_regions')))
    rightCount = list(idList.values_list('right_brain_regions').annotate(the_count=Count('right_brain_regions')))
    time2 = datetime.datetime.now()
    uniLeftCount = []
    uniRightCount = []
    
    #allCounts = {'u':zip(uniList,uniCount), 'l':zip(leftList,leftCount), 'r':zip(rightList,rightCount), 'ul':zip(uniLeftList,uniLeftCount), 'ur':zip(uniRightList,uniRightCount)}
    allCounts = {'u':uniCount, 'l':leftCount, 'r':rightCount, 'ul':uniLeftCount, 'ur':uniRightCount}
    createList = []
    for side, zipList in allCounts.items():
        time3 = datetime.datetime.now()


        for (id, count) in zipList:
#             if id is not None:
#                 region = BrainRegion.objects.get(id=id)
            if id != None:
                createList.append(SearchToRegion(brain_region_id=id, pubmed_search=searchObject, count=count, side=side))
        time4 = datetime.datetime.now()
        print time4 - time3

    SearchToRegion.objects.bulk_create(createList)
    
    print time2 - time1
    print time3 - time2
    print
def pubbrain_search(search):

    try:
        searchObject=PubmedSearch.objects.get(query=search)
    except:
        searchObject=PubmedSearch.create(search)
        searchObject.save()
        
    if searchObject.last_updated is None or (datetime.date.today() - searchObject.last_updated).days > 30:
        time1 = datetime.datetime.now()
        handle=Entrez.esearch(db='pubmed',term=search+'[tiab]',retmax=100000)
        time2 = datetime.datetime.now()
        record = Entrez.read(handle)
        time3 = datetime.datetime.now()
        idList = Pmid.objects.filter(pubmed_id__in=record['IdList'])
        time4 = datetime.datetime.now()
        print
        searchObject.pubmed_ids.add(*idList)
        print
        time5 = datetime.datetime.now()
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
        time6 = datetime.datetime.now()
        
        img = pklsToNifti(searchObject, affine2mm)
        time7 = datetime.datetime.now()
        filename = os.path.join(MEDIA_ROOT, 'temp', search +'.nii.gz')
        time8 = datetime.datetime.now()
        nib.save(img, filename)
        with open(filename) as imgFile:
            searchObject.file = File(imgFile)
            searchObject.last_updated = datetime.date.today()
            searchObject.save()
        os.remove(filename)
        time9 = datetime.datetime.now()
        
        print time2 - time1
        print time3 - time2
        print time4 - time3
        print time5 - time4
        print time6 - time5
        print time7 - time6
        print time8 - time7
        print time9 - time8
        
    return searchObject
    

        
 
# cProfile.runctx("pubbrain_search('memory')", None, locals())
