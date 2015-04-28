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
import django
django.setup()
from pubbrain_app.models import *
from django.db import transaction
from django.db.models import Q
import time
import datetime

def addPmid(id, info):
    entry=Pmid.create(id)
        
    try:
        abstract=info['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
        entry.abstract = abstract.encode('ascii','ignore')
    except:
        pass
    try:
        title = info['MedlineCitation']['Article']['ArticleTitle']
        entry.title = title.encode('ascii','ignore')
    except:
        pass
        
    entry.save()
    return entry

def addPmidRegion(entry, region, syn, leftSyn, rightSyn):
    #checks for whether the  region name, the left version, and the right version are present in the abstract/title 
    # and adds the appropriate relationships
    abstractTitle = (entry.abstract + ' ' + entry.title).lower()
    
    hasLeft = leftSyn in abstractTitle
    hasRight = rightSyn in abstractTitle
#         print abstractTitle
    if hasLeft or hasRight:
        if hasLeft:
            entry.left_brain_regions.add(region)
        if hasRight:
            entry.right_brain_regions.add(region)
        if syn in abstractTitle.replace(leftSyn, '').replace(rightSyn,''):
            entry.uni_brain_regions.add(region)
    else:
        entry.uni_brain_regions.add(region)
    entry.save()
    
def indexIdList(idSet, region, syn, pmidSet):
    #
    set_autocommit(False)
    leftSyn = 'left ' + syn
    rightSyn = 'right ' + syn
    
    # ids that are in the search but not related to region in database need to be added appropriately
    newIds = idSet.difference(pmidSet)
    print 'new ids: ', len(newIds)
    # ids that aren't in the database
    existingIdsQuery = Pmid.objects.filter(pubmed_id__in=newIds)
    existingIds = set([str(x) for (x,) in existingIdsQuery.values_list('pubmed_id')])
#     createIds = set([x for x in newIds if not Pmid.objects.filter(pubmed_id=x)])
    # ids that are in the database but need to be related to the region
    createIds = newIds.difference(existingIds)
    createIdsList = list(createIds)
    #     print createIds, existingIds
    print len(createIds), len(existingIds)
    if createIdsList:
        for i in range(5):
            try:
                handle=Entrez.efetch(db='pubmed',id=createIdsList,retmax=100000,retmode='xml',rettype='abstract') 
                record = Entrez.read(handle)
                for id, info in zip(createIdsList, record):
                    entry = addPmid(id, info)
                    addPmidRegion(entry, region, syn, leftSyn, rightSyn)
                break
            except:
                print 'retry'
        else:
            print syn, ": could not get abstracts/titles" 
            
        
    if existingIdsQuery:
        for entry in existingIdsQuery:
            addPmidRegion(entry, region, syn, leftSyn, rightSyn)
    
    transaction.commit()
    set_autocommit(True)

def index_pubmed(force=False):
    print 'getting pubmed records from scratch'
    errorList = []
    for region in BrainRegion.objects.all():
        if region.last_indexed == None or (datetime.date.today() - region.last_indexed).days > 30 or force:
            print region.name,region.query, region.pk
            
            pmidQuerySet = Pmid.objects.filter(Q(uni_brain_regions=region)|Q(left_brain_regions=region)|Q(right_brain_regions=region))
            pmidSet = set([str(x) for (x,) in pmidQuerySet.values_list('pubmed_id')])
            
            for syn in region.synonyms.split("$"):
                start_time = time.time()
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
                
                idSet = set(record['IdList'])
                print "number of ids %d"%len(idSet)
                
                
                
                indexIdList(idSet, region, syn, pmidSet)
                print("--- %s seconds ---(%s)" % (time.time() - start_time, datetime.datetime.now()))
            
            region.last_indexed=datetime.date.today()
            region.save()
        else:
            print 'using existing results for',region.name
    print 'Errors: ', errorList
    



# syn = 'angular gyrus'
# region = BrainRegion.objects.get(name=syn)
# query = '"' + syn + '"[tiab]'
# handle=Entrez.esearch(db='pubmed',term=query,retmax=100000)
# record = Entrez.read(handle)
# idSet = set(record['IdList'])
# print len(idSet)
# def hey():
#     handle2=Entrez.efetch(db='pubmed',id=idList,retmax=100000,retmode='xml',rettype='abstract') 
#     record2 = Entrez.read(handle2)

profile.run('print index_pubmed(); print')
    