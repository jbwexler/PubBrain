"""
index pubmed for anatomical ontology terms
"""

from Bio import Entrez
from Bio.Entrez import efetch, read
import pickle
from django.db.transaction import set_autocommit, get_autocommit
Entrez.email='poldrack@stanford.edu'
import datetime
import profile
import unicodedata
import django
django.setup()
from pubbrain_app.models import *
from django.db import transaction
from django.db.models import Q


def addOrGetPmid(id, syn):
    # returns Pmid object matching id. if no object exists, creates a new object and adds the abstract and title
    items=Pmid.objects.filter(pubmed_id=id)
    if not items.exists():
        entry=Pmid.create(id)
        for i in range(3):
            try:
                handle=Entrez.efetch(db='pubmed',id=id,retmax=100000,retmode='xml',rettype='abstract')
                abstractRecord = Entrez.read(handle)
                break
            except:
                print 'retry'
                pass
        else:
            print syn, ": could not get abstract/title"

        try:
            abstract=abstractRecord[0]['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
            entry.abstract = abstract.encode('ascii', 'ignore')
        except:
            pass
        try:
            title = abstractRecord[0]['MedlineCitation']['Article']['ArticleTitle']
            entry.title = title.encode('ascii', 'ignore')
        except:
            pass
        entry.save()
    else:
        entry=items[0]
    return entry

def addPmidRegion(entry, region, syn, leftSyn, rightSyn):
    #checks for whether the  region name, the left version, and the right version are present in the abstract/title 
    # and adds the appropriate relationships
    abstractTitle = (entry.abstract + ' ' + entry.title).lower()
    
    hasLeft = leftSyn in abstractTitle
    hasRight = rightSyn in abstractTitle
#         print abstractTitle
    if hasLeft or hasRight:
        print abstractTitle
        if hasLeft:
            print 'left'
            entry.left_brain_regions.add(region)
        if hasRight:
            print 'right'
            entry.right_brain_regions.add(region)
        if syn in abstractTitle.replace(leftSyn, '').replace(rightSyn,''):
            print 'uni'
            entry.uni_brain_regions.add(region)
    else:
        entry.uni_brain_regions.add(region)
    entry.save()
    
def indexIdList(idList, region, syn):
    #
    set_autocommit(False)
    leftSyn = 'left ' + syn
    rightSyn = 'right ' + syn
    pmidObjectSet = Pmid.objects.filter(Q(uni_brain_regions=region)|Q(left_brain_regions=region)|Q(right_brain_regions=region))
    pmidSet = pmidObjectSet.values_list('pubmed_id')
    for id in idList:
        #print id
        entry = addOrGetPmid(id, syn)
        if (id) not in pmidSet:
            addPmidRegion(entry, region, syn, leftSyn, rightSyn)
           
    transaction.commit()
    set_autocommit(True)

def index_pubmed(force=False):
    print 'getting pubmed records from scratch'
    errorList = []
    for region in BrainRegion.objects.all():
        if region.last_indexed == None or (datetime.date.today() - region.last_indexed).days > 30 or force:
            print region.name,region.query, region.pk
            # get list of all related pmids
            relatedIds = region.uni_pmids.clear()
            region.left_pmids.clear()
            region.right_pmids.clear()
            

            for syn in region.synonyms.split("$"):
                query = '"' + syn + '"[tiab]'
                print query
                for i in range(3):
                    try:
                        handle=Entrez.esearch(db='pubmed',term=query,retmax=100000)
                        record = Entrez.read(handle)
                        break
                    except:
                        pass
                else:
                    print region, ": could not get search results"
                    errorList.append(region.name)
                
                idList = record['IdList']
                print "number of ids %d"%len(idList)
                
                indexIdList(idList, region, syn)
            
            region.last_indexed=datetime.date.today()
            region.save()
        else:
            print 'using existing results for',region.name
    print 'Errors: ', errorList
    
# def addAbstractsAndTitles():
#     #gets Abstracts and titles for all Pmids
#     for region in [x for x in Pmid.objects.all() if not x.title and not x.abstract]:
#         pass


# profile.run('print index_pubmed(); print')
    
index_pubmed(True)
# manual_transaction(record, BrainRegion.objects.get(name='piriform cortex'))
# profile.run("manual_transaction(record, BrainRegion.objects.get(name='hippocampus'), ''); print")
# profile.run("manual_transaction(record, BrainRegion.objects.get(name='piriform cortex'), ''); print")


