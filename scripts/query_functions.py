# various functions that are useful for querying the database

from pubbrain_app.models import *
from abstract_rendering.numeric import Count
import networkx as nx

def showChildAndPar():
    # shows relationships between regions that are both parents/children of each other
    # ex: cerebral cortex is parent and child of cerebral hemisphere
    for region in BrainRegion.objects.all():
        intersection = set(region.allParents.all()).intersection(set(region.allChildren.all()))
        if intersection:
            print region.name 
            print [x.name for x in intersection]

# def bestParent(region):
#     parents = region.allParents.all()
#     best = ''
#     for i in range(len(parents)-1):
#         parent = parents[i]
#         nextParent = parents[i+1]
#         if parent == nextParent:
#             continue
#         elif nextParent in allAbove(parent):
#             best = parent
#         elif parent in allAbove(nextParent):
#             best = nextParent
#         else:
#             print 'error'
#     return best
        
def createNetx():
    # creates a networkx digraph from ontology in database
    graph = nx.DiGraph()
    for region in BrainRegion.objects.all():
        graph.add_node(region.name, {'name':region.name})
    for region in BrainRegion.objects.all():
        for parent in region.allParents.all():
            graph.add_edge(parent.name, region.name)
    return(graph) 
            
        
# def addGenRecur(region, direction, count=0):
#     if direction == 'up':
#         count -= 1
#     elif direction == 'down':
#         count += 1
#     print region.name, count
#     region.generation = count
#     region.save()
#     for parent in [x for x in region.allParents.all() if x.generation is None]:
#         print "parents: "+parent.name
#         addGenRecur(parent, 'up', count=count)
#     for child in [x for x in region.allChildren.all() if x.generation is None]:
#         print "children: "+child.name
#         addGenRecur(child, 'down', count=count)

def allAbove(region):
    # searches parents recursively to get a set of all the regions above the specified region
    above = set([region])
    print region.name
    for parent in region.allParents.all():
        print "parent: ", parent.name
        above.update(allAbove(parent))
    return above

def addGenAll(startRegion):
    for r in BrainRegion.objects.all():
        r.generation = None
        r.save()
    addGenRecur(startRegion, 'down', -1)

def childGenCount(region, count = 0):
    count += 1
#     print count, '_'*count, region.name
    if region.allChildren.count() == 0:
        print 'end'
        return count
    else:
        counts = []
        for child in region.allChildren.all():
            counts.append(childGenCount(child, count))

        return max(counts)

def parentGenCount(region, count = 0):
    count += 1
#     print count, '_'*count, region.name
    if region.allParents.count() == 0:
        print 'end'
        return count
    else:
        counts = []
        
        for parent in region.allParents.all():
            counts.append(parentGenCount(parent, count))
            print 
        return max(counts)
    
def printSynRegions():
    # prints regions that are duplicates or whose synonyms already exist
    
    for region in BrainRegion.objects.exclude(synonyms=None):
        synonyms = region.synonyms.split("$")
        synonyms.remove(region.name)
        for syn in synonyms:
            fil = BrainRegion.objects.filter(name=syn)
            if fil:
                print [x.name for x in fil]
    
    for region in BrainRegion.objects.all():
        fil = BrainRegion.objects.filter(name=region.name)
        if len(fil) > 1:
            print [x.name for x in fil] 

