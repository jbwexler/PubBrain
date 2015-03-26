"""
makes an excel spreadsheet showing pairs of regions and the atlas region the are mapped to, along with the number of Pmids for that region.
"""

from pubbrain_app.models import BrainRegion, Pmid, AtlasPkl
import os.path
from boto.s3.multipart import Part
import xlwt
from pubbrain_app.models import BrainRegion

def mapOntReverse(outputFile):
    excel = xlwt.Workbook()
    sheet1 = excel.add_sheet('sheet1')
    
    
    count = 0
    for region in BrainRegion.objects.all():
        idCount = len(region.pmid_set.all())
        if region.atlasregions.all():
            for atlasRegion in region.atlasregions.all():
                sheet1.write(count,0, region.name)
                sheet1.write(count,1, atlasRegion.name)
                sheet1.write(count,2, atlasRegion.atlas_voxels)
                sheet1.write(count,3, idCount)
                count += 1
        else:
            sheet1.write(count,0, region.name)
            sheet1.write(count,3, idCount)
            count += 1
    
    
            
    excel.save(outputFile)  
    print 'done'

def mappedAtlasRegions(outputFile):
    excel = xlwt.Workbook()
    sheet1 = excel.add_sheet('sheet1')
    
    count = 0
    for object in AtlasPkl.objects.all():
        if object.brainregions.all():
            for BrainRegion in object.brainregions.all():
                sheet1.write(count,0, object.atlas)
                sheet1.write(count,1, object.name)
                sheet1.write(count,2, BrainRegion.name)
                count += 1
        else:
            sheet1.write(count,0, object.atlas)
            sheet1.write(count,1, object.name)
            count += 1
            
    excel.save(outputFile)  
    print 'done'

#mapOntReverse('/Users/jbwexler/poldrack_lab/cs/other/mappings7.xls')

mappedAtlasRegions('/Users/jbwexler/poldrack_lab/cs/other/atlasmappings5.xls')