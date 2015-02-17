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

def index_pubmed(force=False):
    print 'getting pubmed records from scratch'
    
    for brainRegion in models.BrainRegion.objects.all():
        print [x.name for x in brainRegion.atlasregions.all()]
        if (brainRegion.last_indexed - datetime.date.today()).days > 30 or force or len(brainRegion.atlasregions.all())==0:
            print brainRegion.name,brainRegion.query
            handle=Entrez.esearch(db='pubmed',term=brainRegion.query,retmax=100000)
            record = Entrez.read(handle)
            print "number of ids %d"%len(record['IdList'])
            
            manual_transaction(record, brainRegion)

                 
            brainRegion.last_indexed=datetime.date.today()
        else:
            print 'using existing results for',brainRegion.name

            
            
profile.run('print index_pubmed(); print')
