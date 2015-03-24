"""
index pubmed for anatomical ontology terms
"""

from Bio import Entrez
from Bio.Entrez import efetch, read
import pickle
from pubbrain_app.models import BrainRegion
Entrez.email='poldrack@stanford.edu'
import datetime
import profile

import django
django.setup()
from pubbrain_app import models
from django.db import transaction
from django.db.models import Q


@transaction.commit_manually
def manual_transaction(record, brainRegion, side):
    regionName = brainRegion.name
    leftRegion = 'left' + regionName
    rightRegion = 'right' + regionName
    
    for id in record['IdList']:
        #print id
        items=models.Pmid.objects.filter(pubmed_id=id)
        if not items.exists():
            entry=models.Pmid.create(id)
            handle=Entrez.efetch(db='pubmed',id=id,retmax=100000,retmode='xml',rettype='abstract')
            abstractRecord = Entrez.read(handle)
            try:
                abstract=str(abstractRecord[0]['MedlineCitation']['Article']['Abstract']['AbstractText'][0])
                entry.abstract = abstract
            except KeyError:
                print "couldn't get abstract"
            try:
                title = str(abstractRecord[0]['MedlineCitation']['Article']['ArticleTitle'])
                abstract.title = title
            except KeyError:
                print "coudn't get title"
            entry.save()
        else:
            entry=items[0]
        
        
        
        abstractTitle = (entry.abstract + ' ' + entry.title).lower()
        
        hasLeft = leftRegion in abstractTitle
        hasRight = rightRegion in abstractTitle
        
        if hasLeft or hasRight:
            if hasLeft:
                entry.left_brain_regions.add(brainRegion)
            if hasRight:
                entry.right_brain_regions.add(brainRegion)
            if regionName not in abstractTitle.replace(leftRegion, '').replace(rightRegion,''):
                entry.uni_brain_regions.add(brainRegion)
            
#         if side == 'left ':
#             entry.left_brain_regions.add(brainRegion)
#         elif side =='right ':
#             entry.right_brain_regions.add(brainRegion)
#         else:
#             entry.uni_brain_regions.add(brainRegion)
            
    transaction.commit()
    
@transaction.commit_manually
def manual_transaction2(record, brainRegion, side):
    for id in record['IdList']:
        #print id
        try:
            entry=models.Pmid.objects.get(pubmed_id=id)
        except:
            entry=models.Pmid.create(id)
            entry.save()
        if side == 'left ':
            entry.left_brain_regions.add(brainRegion)
        elif side =='right ':
            entry.right_brain_regions.add(brainRegion)
        else:
            entry.uni_brain_regions.add(brainRegion)
            
    transaction.commit()

def index_pubmed(force=False):
    print 'getting pubmed records from scratch'
    errorList = []
    for region in models.BrainRegion.objects.all():
        if region.last_indexed == None or (datetime.date.today() - region.last_indexed).days > 30 or force:
            print region.name,region.query, region.pk
            # get list of all related pmids
            relatedIds = region.uni_pmids.clear()
            region.left_pmids.clear()
            region.right_pmids.clear()
            for syn in region.synonyms.split("$"):
                for side in ['', 'left ', 'right ']:
                    query = '"' + side + syn + '"[tiab]'
                    print query
                    try:
                        handle=Entrez.esearch(db='pubmed',term=query,retmax=100000)
                        record = Entrez.read(handle)
                    except:
                        errorList.append(region.name)
                        continue
                    print "number of ids %d"%len(record['IdList'])
                
                    manual_transaction(record, region, side)

                 
            region.last_indexed=datetime.date.today()
            region.save()
        else:
            print 'using existing results for',region.name
    print 'Errors: ', errorList
    
def addAbstracts():
    #gets Abstracts and titles for all Pmids
    for region in [x for x in BrainRegion.objects.all() if not x.title and not x.abstract]:
        
    

            
# profile.run("manual_transaction(record, BrainRegion.objects.get(name='hippocampus'), ''); print")
profile.run("manual_transaction(record, BrainRegion.objects.get(name='piriform cortex'), ''); print")
# profile.run('print index_pubmed(True); print')
