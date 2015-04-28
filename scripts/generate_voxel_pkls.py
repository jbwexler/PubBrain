'''
generates a .pkl file containing an array of corresponding voxels for each region in every FSL atlas
and places it in scripts/pickle_files/voxels.
'''

import nibabel
import xml.etree.ElementTree as ET
import numpy as np
import numpy.linalg as npl
import nibabel as nib
import os.path
import cPickle as pickle
from __builtin__ import True


def createPkl(pklDir, region, voxels):
    pklFile = region.replace('/', '_').replace(' ', '_') + '.pkl'
    with open(os.path.join(pklDir, pklFile),'wb') as output:
        pickle.dump(voxels, output, -1)
        
def convertTo2mm(atlas_mask, aff):
    voxels = np.where(atlas_mask)
    new_mask = np.zeros((91,109,91))
    voxelsmm = [[],[],[]]
    affine2mm = np.array([
            [-2, 0, 0, 90],
            [0, 2, 0, -126],
            [0, 0, 2, -72],
            [0, 0, 0, 1]])
    for i in range(len(voxels[0])):
        XYZ = [voxels[0][i],voxels[1][i],voxels[2][i]]
        XYZmm = nibabel.affines.apply_affine(aff, XYZ)
        XYZnew = nib.affines.apply_affine(npl.inv(affine2mm), XYZmm)
        new_mask[XYZnew[0],XYZnew[1],XYZnew[2]] = True
    
        
def getAtlasVoxels(intensity, image, voxelSize):
    image_data = image.get_data()
    aff = image.get_affine()
    atlas_mask = np.zeros(image_data.shape)
    atlas_mask[image_data==intensity] = True
    print atlas_mask.sum()
    # need to convert to 2mm if not already 2mm
    if voxelSize != 2:
        atlas_mask2mm = convertTo2mm(atlas_mask, aff) 
        return np.where(atlas_mask2mm)
    else:
        return np.where(atlas_mask)
    
        
def generateAtlasPkls(atlasXML, dir = '/usr/local/fsl/data/atlases', indexIntensityDiff = 1):
    pklDir = 'pickle_files/atlas_region_voxels/' + os.path.splitext(atlasXML)[0]
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
    list1mm = [image for image in summaryImageList if '1mm' in image]
    if list2mm != []:
        summaryImageFile = list2mm[0]
        voxelSize = 2
    elif list1mm != []:
        summaryImageFile = list1mm[0]
        voxelSize = 1
    else:
        summaryImageFile = summaryImageList[0] 
        voxelSize = 'other'
    
    image_name = summaryImageFile[1:] + '.nii.gz'
    image=nibabel.load(os.path.join(dir, image_name))

    for line in root.find('data').findall('label'):
        name = line.text.replace("'",'').rstrip(' ').lower()
        # most atlases have an intensity that is one greater than their index, thus it is necessary to add
        # the indexIntensityDiff (usually is 1). in some atlases the indices and intensities are equal so
        # indexIntensityDiff should be set to 0
        intensity = int(line.get('index')) + indexIntensityDiff
        voxels = getAtlasVoxels(intensity, image, voxelSize)
        createPkl(pklDir, name, voxels)

#list of atlases whose intensities and indices are the same (instead of difference of 1)
diffZeroList = ['Striatum-Structural.xml', 'Talairach.xml']

np.set_printoptions(threshold=np.nan)
for file in os.listdir('/usr/local/fsl/data/atlases'):
    if '.xml' in file:
        print file
        if file in diffZeroList:
            generateAtlasPkls(file,indexIntensityDiff = 0)
        else:
            generateAtlasPkls(file)
            

