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


@transaction.commit_manually
def manual_transaction(record, brainRegion, side):
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
            region.uni_pmids.clear()
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

            
            
profile.run('print index_pubmed(); print')
