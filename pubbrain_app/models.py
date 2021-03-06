from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models.fields.related import ManyToManyField
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_delete, pre_delete
import os
import operator


# represents an atlas region
class AtlasPkl(models.Model):
    name=models.TextField(max_length=1000)
    atlas=models.TextField(max_length=1000, blank=True, null=True)
    uni_pkl=models.TextField(max_length=1000, blank=True, null=True)
    left_pkl=models.TextField(max_length=1000, blank=True, null=True)
    right_pkl=models.TextField(max_length=1000, blank=True, null=True)
    @classmethod
    def create(cls, name):
        entry = cls(name=name)
        return entry

# represents a brain region from the ontology   
class BrainRegion(MPTTModel):
    
    # name of the region - from the ontology
    name=models.TextField(max_length=1000)
    
    # the pubmed query for the region
    query=models.CharField(max_length=255)
    
    # is this a native region in the atlas?
    has_pkl=models.BooleanField(default=False)
    
    # corresponding AtlasPkl objects, from which the pkl files can be taken
    atlas_regions=models.ManyToManyField(AtlasPkl, related_name='brainregions')
    
    # pkls that associated with unilateral, left or right sides, respectively
    uni_pkls = models.CharField(max_length=500, blank=True)
    left_pkls = models.CharField(max_length=500, blank=True)
    right_pkls = models.CharField(max_length=500, blank=True)
    
    # string comprised of a '$' delimited list of synonyms
    synonyms=models.TextField(blank=True, null=True)
    
    # all parents
    allParents=models.ManyToManyField('self', blank=True, symmetrical=False, related_name='allChildren')
    
    # best parent, which will bes used in the hierarchical graph
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    # region(s) that best represent this region (can be itself). 
    mapped_regions=models.ManyToManyField('self', blank=True,symmetrical=False)
    
    # generation level, highest on the hierarchy (ie 'brain' or 'encephalon') should be closest to 0
    topological_sort = models.IntegerField(null=True, blank=True)
    
    # name in NIF, Uberon and FMA, if present
    # note: region from ontology may contain the words 'right' or 'left', which won't be present here
    NIF_name = models.CharField(max_length=255, blank=True)
    Uberon_name = models.CharField(max_length=255, blank=True)
    FMA_name = models.CharField(max_length=255, blank=True)
    
    last_indexed=models.DateField(null=True, blank=True)
    
    @classmethod
    def create(cls, name):
        region = cls(name=name)
        return region

    def sumPmids(self):
        sum=self.uni_pmids.all().count() + self.left_pmids.all().count() + self.right_pmids.all().count()
        return sum
    
    class MPTTMeta:
        order_insertion_by = ['name']

# represents a PubMed ID

class Pmid(models.Model):
    pubmed_id=models.IntegerField(db_index=True)
    date_added=models.DateField(auto_now_add=True)
    # link to the brain regions mentioned in the abstract
    uni_brain_regions=models.ManyToManyField(BrainRegion, blank=True, related_name='uni_pmids')
    left_brain_regions=models.ManyToManyField(BrainRegion, blank=True, related_name='left_pmids')
    right_brain_regions=models.ManyToManyField(BrainRegion, blank=True, related_name='right_pmids')
    title=models.CharField(max_length=10000,default='')
    abstract = models.TextField(max_length=100000, default='')
    
    @classmethod
    def create(cls, pmid):
        entry = cls(pubmed_id=pmid)
        return entry
    


# represents a saved search
class PubmedSearch(models.Model):
    date_added=models.DateField(auto_now_add=True)
    file=models.FileField(null=True, blank=True)
    last_updated=models.DateField(blank=True, null=True)
    # the pubmed query for the region
    query=models.CharField(max_length=255)
    pubmed_ids=models.ManyToManyField(Pmid)
    brain_regions=models.ManyToManyField(BrainRegion, blank=True, through='SearchToRegion')
    @classmethod
    def create(cls, query):
        result = cls(query=query)
        return result
    def mappedRegionsList(self):
        querySet = self.searchtoregion_set.prefetch_related('brain_region').all()
        uniSet = querySet.filter(side='u').values_list('brain_region__mapped_regions__name','count')
        leftSet = querySet.filter(side='l').values_list('brain_region__mapped_regions__name','count')
        rightSet = querySet.filter(side='r').values_list('brain_region__mapped_regions__name','count')
        setList = [(uniSet, 'uni '),(leftSet,'left '),(rightSet,'right ')]
        countDict = {}
        for set, side in setList:
            for (name, count) in set:
                if name:
                    countDict[side+name] = 0
            for (name, count) in set:
                if name:
                    countDict[side+name] += count
        sorted_x = sorted(countDict.items(), key=operator.itemgetter(1))
        return sorted_x

@receiver(pre_delete, sender=PubmedSearch)
def delSearchImg(sender, instance, **kwargs):
    if instance.file:
        path = instance.file.path
        try:
            os.remove(path)
        except OSError:
            print 'Could not find file: %s' % path

class SearchToRegion(models.Model):
    SIDES = (
        ('l', 'left'),
        ('r', 'right'),
        ('u', 'uni'),
        ('ul', 'uni-left'),
        ('ur', 'uni-right'),
        )
    pubmed_search = models.ForeignKey(PubmedSearch)
    brain_region = models.ForeignKey(BrainRegion)
    count = models.IntegerField(null=True, blank=True)
    side = models.CharField(max_length=2, choices=SIDES)
