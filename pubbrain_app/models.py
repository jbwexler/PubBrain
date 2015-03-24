from django.db import models


# represents an atlas region
class AtlasPkl(models.Model):
    side_choices = (
    ('left', 'left'),
    ('right', 'right'),
    ('unilateral', 'unilateral'))
    
    name=models.TextField(max_length=1000)
    atlas=models.TextField(max_length=1000, blank=True, null=True)
    pkl=models.TextField(max_length=1000, blank=True, null=True)
    side=models.TextField(max_length=1000, choices=side_choices, null=True, blank=True)
    @classmethod
    def create(cls, pkl):
        entry = cls(pkl=pkl)
        return entry

# represents a brain region from the ontology   
class BrainRegion(models.Model):
    
    # name of the region - from the ontology
    name=models.TextField(max_length=1000)
    
    # the pubmed query for the region
    query=models.CharField(max_length=255)
    
    # is this a native region in the atlas?
    is_atlasregion=models.BooleanField(default=False)
    
    # if so, save the voxels associated with the region (as a cPickle)
    uni_atlas_voxels=models.ManyToManyField(AtlasPkl, related_name='uni_brainregions')
    left_atlas_voxels=models.ManyToManyField(AtlasPkl, related_name='left_brainregions')
    right_atlas_voxels=models.ManyToManyField(AtlasPkl, related_name='right_brainregions')
    
    synonyms=models.TextField(blank=True, null=True)
    # parent-child relations in the partonomy
    parents=models.ManyToManyField('self', null=True, blank=True, symmetrical=False, related_name='children')
    
    # a list of the atlas areas associated with this term
    # if is_atlasregion==True then this will be same as the name
    # in other cases, it may refer to a single parent
    # or to multiple children (e.g., "frontal lobe" is represented
    # by a number of specific parts of the frontal lobe in the atlas)
    atlasregions=models.ManyToManyField('self', null=True, blank=True,symmetrical=False)
    
    
    last_indexed=models.DateField(null=True, blank=True)
    
    @classmethod
    def create(cls, name):
        region = cls(name=name)
        return region


# represents a PubMed ID

class Pmid(models.Model):
    pubmed_id=models.IntegerField(max_length=20, db_index=True)
    date_added=models.DateField(auto_now_add=True,auto_now=True)
    # link to the brain regions mentioned in the abstract
    uni_brain_regions=models.ManyToManyField(BrainRegion, null=True, blank=True, related_name='uni_pmids')
    left_brain_regions=models.ManyToManyField(BrainRegion, null=True, blank=True, related_name='left_pmids')
    right_brain_regions=models.ManyToManyField(BrainRegion, null=True, blank=True, related_name='right_pmids')
    title=models.CharField(max_length=255,default='')
    abstract = models.CharField(max_length=10000, default='')
    
    @classmethod
    def create(cls, pmid):
        entry = cls(pubmed_id=pmid)
        return entry


# represents a saved search
class PubmedSearch(models.Model):
    date_added=models.DateField(auto_now_add=True,auto_now=True)
    filename=models.CharField(max_length=255) 
    date_file_saved=models.DateField(auto_now_add=True,auto_now=True)
    # the pubmed query for the region
    query=models.CharField(max_length=255)
    pubmed_ids=models.ManyToManyField(Pmid)
    @classmethod
    def create(cls, query):
        result = cls(query=query)
        return result


