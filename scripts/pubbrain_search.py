from Bio import Entrez
from Bio.Entrez import efetch, read
import pickle
from pubbrain_app.models import BrainRegion
Entrez.email='poldrack@stanford.edu'
import datetime
import profile
import os
import django
django.setup()
from pubbrain_app import models
from django.db import transaction
# from nipy.labs.viz import plot_map, mni_sform, coord_transform
import numpy as np
import nibabel as nib
import numpy.linalg as npl
    


def arrayToText(data):
    with file('/Users/jbwexler/poldrack_lab/cs/other/array.txt', 'w') as outfile:
        outfile.write('# Array shape: {0}\n'.format(data.shape))
        for data_slice in data:
            np.savetxt(outfile, data_slice, fmt='%-7.2f')
            outfile.write('# New slice\n')

@transaction.commit_manually
def manual_transaction(record, brainRegion):
    for id in record['IdList']:
        #print id
        try:
            entry=models.Pmid.objects.get(pubmed_id=id)
        except:
            entry=models.Pmid.create(id)
            entry.save()
            entry.brain_regions_named.add(brainRegion)
    transaction.commit()

# def visualize(voxels):
#     mni_sform_inv = np.linalg.inv(mni_sform)
    

def pklsToNifti(allFreqDict, aff):
    
    sumArray = np.zeros((91,109,91))
    
    for side, dict in allFreqDict.items():
        for region, freq in dict.items():
            if side == 'left':
                try:
                    pickles = [x.pkl for x in region.left_atlas_voxels.all]
                except:
                    pickles = [x.pkl for x in region.uni_atlas_voxels.all]

            elif side == 'right':
                try:
                    pickles = [x.pkl for x in region.right_atlas_voxels.all]
                except:
                    pickles = [x.pkl for x in region.uni_atlas_voxels.all]
            else:
                try:
                    pickles = [x.pkl for x in region.uni_atlas_voxels.all]
                except:
                    pickles = [x.pkl for x in region.uni_atlas_voxels.all] + [x.pkl for x in region.right_atlas_voxels.all]
                    
                    
            if region.atlas_voxels:
                with open(os.path.join(os.getcwd(),'pickle_files/voxels', region.atlas_voxels),'rb') as input:
                    voxels = pickle.load(input)
    
                for i in range(len(voxels[0])):
                    XYZmm = [voxels[0][i],voxels[1][i],voxels[2][i]]
                    XYZ = nib.affines.apply_affine(npl.inv(aff), XYZmm)
                    sumArray[XYZ[0], XYZ[1], XYZ[2]] += freq
                    if region.name == 'fusiform gyrus':
                        print XYZ
#     arrayToText(sumArray)
    img = nib.Nifti1Image(sumArray, affine=aff)
    return img
    
def pubbrain_search(search):

    try:
        searchObject=models.PubmedSearch.objects.get(query=search)
    except:
        searchObject=models.PubmedSearch.create(query=search)
        searchObject.save()
    handle=Entrez.esearch(db='pubmed',term=search,retmax=100000)
    record = Entrez.read(handle)
    
    uniRegFreq = {}
    leftRegFreq = {}
    rightRegFreq = {}

    
    for id in record['IdList']:
#         print id
        try:
            idObject = models.Pmid.objects.get(pubmed_id=id)
        except:
            continue
        
        uniAtlasRegions = set([region for region in idObject.uni_brainregions.all()])
        leftAtlasRegions = set([region for region in idObject.left_brainregions.all()])
        rightAtlasRegions = set([region for region in idObject.right_brainregions.all()])

        for region in uniAtlasRegions:
            for isAtlasRegion in region.atlasregions.all():
                if uniRegFreq.get(isAtlasRegion) == None:
                    uniRegFreq[isAtlasRegion] = 1
                else:
                    uniRegFreq[isAtlasRegion] += 1
                
        for region in leftAtlasRegions:
            for isAtlasRegion in region.atlasregions.all():
                if leftRegFreq.get(isAtlasRegion) == None:
                    leftRegFreq[isAtlasRegion] = 1
                else:
                    leftRegFreq[isAtlasRegion] += 1
                
        for region in rightAtlasRegions:
            for isAtlasRegion in region.atlasregions.all():
                if rightRegFreq.get(isAtlasRegion) == None:
                    rightRegFreq[isAtlasRegion] = 1
                else:
                    rightRegFreq[isAtlasRegion] += 1
    
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
    
    
    allFreqDict = {'uni':uniRegFreq, 'left':leftRegFreq, 'right':rightRegFreq}
    img = pklsToNifti(allFreqDict, affine2mm)
    nib.save(img, os.path.join('/Users/jbwexler/poldrack_lab/cs/other', search + '.nii.gz'))
    

        
 
 
pubbrain_search('prosopagnosia')


    
#     if (brainRegion.last_indexed - datetime.date.today()).days > 30
#         print brainRegion.name,brainRegion.query
#         handle=Entrez.esearch(db='pubmed',term=brainRegion.query,retmax=100000)
#         record = Entrez.read(handle)
#         print "number of ids %d"%len(record['IdList'])
#         
#         manual_transaction(record, brainRegion)
# 
#              
#         brainRegion.last_indexed=datetime.date.today()
#     else:
#         print 'using existing results for',brainRegion.name
