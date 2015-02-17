'''
generates a .pkl file containing an array of corresponding voxels for each region in every FSL atlas
and places it in scripts/pickle_files/voxels.
'''

import nibabel
import xml.etree.ElementTree as ET
import numpy
import os.path
import cPickle as pickle
from __builtin__ import True


def createPkl(pklDir, region, voxels):
    pklFile = region.replace('/', '_').replace(' ', '_') + '.pkl'
    with open(os.path.join(pklDir, pklFile),'wb') as output:
        pickle.dump(voxels, output, -1)
        
def getAtlasVoxels(intensity, image):
    image_data = image.get_data()
    aff = image.get_affine()
    atlas_mask = numpy.zeros(image_data.shape)
        
    atlas_mask[image_data==intensity] = True
    if atlas_mask.sum() != 0:
        voxels = numpy.where(atlas_mask)
        voxelsmm = [[],[],[]]
        for i in range(len(voxels[0])):
            XYZ = [voxels[0][i],voxels[1][i],voxels[2][i]]
            XYZmm = nibabel.affines.apply_affine(aff, XYZ)
            voxelsmm[0].append(XYZmm[0])
            voxelsmm[1].append(XYZmm[1])
            voxelsmm[2].append(XYZmm[2])

        return voxelsmm
        
def generateAtlasPkls(atlasXML, dir = '/Applications/fmri_progs/fsl/data/atlases/', indexIntensityDiff = 1):
    pklDir = 'pickle_files/voxels/' + os.path.splitext(atlasXML)[0]
    try:
        os.stat(pklDir)
    except:
        os.mkdir(pklDir)   
    tree = ET.parse(os.path.join(dir, atlasXML))
    root = tree.getroot()
    summaryImageList = []
    summaryImageFile = ''
    root_header = root.find('header')
    for images in root_header.findall('images'):
        summaryImageList.append(images.find('summaryimagefile').text)
    
    list2mm = [image for image in summaryImageList if '2mm' in image]
    list1mm = [image for image in summaryImageList if '2mm' in image]
    
    if list2mm != []:
        summaryImageFile = list2mm[0]
    elif list1mm != []:
        summaryImageFile = list1mm[0]
    else:
        summaryImageFile = summaryImageList[0] 
    
    image_name = summaryImageFile[1:] + '.nii.gz'
    image=nibabel.load(os.path.join(dir, image_name))

    for line in root.find('data').findall('label'):
        name = line.text.replace("'",'').rstrip(' ').lower()
        # most atlases have an intensity that is one greater than their index, thus it is necessary to add
        # the indexIntensityDiff (usually is 1). in some atlases the indices and intensities are equal so
        # indexIntensityDiff should be set to 0
        intensity = int(line.get('index')) + indexIntensityDiff
        voxels = getAtlasVoxels(intensity, image)
        createPkl(pklDir, name, voxels)

#list of atlases whose intensities and indices are the same (instead of difference of 1)
diffZeroList = ['Striatum-Structural.xml', 'Talairach.xml']


for file in os.listdir('/Applications/fmri_progs/fsl/data/atlases/'):
    if '.xml' in file:
        print file
        if file in diffZeroList:
            generateAtlasPkls(file,indexIntensityDiff = 0)
        else:
            generateAtlasPkls(file)
            

