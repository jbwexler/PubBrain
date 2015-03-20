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
        if object.uni_brainregions.all() or object.left_brainregions.all() or object.right_brainregions.all():
            if object.uni_brainregions.all():
                for BrainRegion in object.uni_brainregions.all():
                    sheet1.write(count,0, object.atlas)
                    sheet1.write(count,1, object.name)
                    sheet1.write(count,2, object.side)
                    sheet1.write(count,3, BrainRegion.name)
                    sheet1.write(count,4, 'unilateral')
                    count += 1
            elif object.left_brainregions.all():
                for BrainRegion in object.left_brainregions.all():
                    sheet1.write(count,0, object.atlas)
                    sheet1.write(count,1, object.name)
                    sheet1.write(count,2, object.side)
                    sheet1.write(count,3, BrainRegion.name)
                    sheet1.write(count,4, 'left')
                    count += 1
            else:
                for BrainRegion in object.right_brainregions.all():
                    sheet1.write(count,0, object.atlas)
                    sheet1.write(count,1, object.name)
                    sheet1.write(count,2, object.side)
                    sheet1.write(count,3, BrainRegion.name)
                    sheet1.write(count,4, 'right')
                    count += 1
        else:
            sheet1.write(count,0, object.atlas)
            sheet1.write(count,1, object.name)
            sheet1.write(count,2, object.side)
            count += 1
            
    excel.save(outputFile)  
    print 'done'

#mapOntReverse('/Users/jbwexler/poldrack_lab/cs/other/mappings7.xls')

mappedAtlasRegions('/Users/jbwexler/poldrack_lab/cs/other/atlasmappings4.xls')