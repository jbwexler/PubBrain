from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models.fields.related import ManyToManyField


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
    allParents=models.ManyToManyField('self', null=True, blank=True, symmetrical=False, related_name='allChildren')
    
    # best parent, which will bes used in the hierarchical graph
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    # region(s) that best represent this region (can be itself). 
    mapped_regions=models.ManyToManyField('self', null=True, blank=True,symmetrical=False)
    
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
    pubmed_id=models.IntegerField(max_length=20, db_index=True)
    date_added=models.DateField(auto_now_add=True,auto_now=True)
    # link to the brain regions mentioned in the abstract
    uni_brain_regions=models.ManyToManyField(BrainRegion, null=True, blank=True, related_name='uni_pmids')
    left_brain_regions=models.ManyToManyField(BrainRegion, null=True, blank=True, related_name='left_pmids')
    right_brain_regions=models.ManyToManyField(BrainRegion, null=True, blank=True, related_name='right_pmids')
    title=models.CharField(max_length=10000,default='')
    abstract = models.TextField(max_length=100000, default='')
    
    @classmethod
    def create(cls, pmid):
        entry = cls(pubmed_id=pmid)
        return entry
    


# represents a saved search
class PubmedSearch(models.Model):
    date_added=models.DateField(auto_now_add=True)
    filename=models.CharField(max_length=255) 
    last_updated=models.DateField(blank=True, null=True)
    # the pubmed query for the region
    query=models.CharField(max_length=255)
    pubmed_ids=models.ManyToManyField(Pmid)
    brain_regions=models.ManyToManyField(BrainRegion, null=True, blank=True, through='SearchToRegion')
    @classmethod
    def create(cls, query):
        result = cls(query=query)
        return result

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
