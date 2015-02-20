"""
converts the FMA ontology into a networkx graph and saves the graph object as a .pkl file. using a networkx graph to find parents, children, etc. is much, much faster 
for our purposes than using rdflib to do a SPARQL query on the .owl.
update: now that there are separate queries checking for parent relationships and child relationships, using the reasoner on the owl file is no longer necessary
"""

import rdflib
import nibabel
import os.path
import networkx as nx
import cPickle as pickle
import timeit


def storeFMAasGraph(owlPath, pklFile, pklDir = ''):
    t = timeit.Timer
    g = rdflib.Graph()
    g.load(owlPath)
    netx = nx.DiGraph()
    
    # query owl file for all regions that are subclasses of birnlex_1167 (aka 'regional part of brain')
    allQuery = g.query(
               """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX fma: <http://purl.org/sig/ont/fma/>
                SELECT ?region ?regionlabel
                WHERE { 
                ?region rdfs:subClassOf+ ?head.
                {?head fma:preferred_name "Segment of brain"^^<http://www.w3.org/2001/XMLSchema#string>}
                UNION {?head fma:preferred_name "Region of cerebral cortex"^^<http://www.w3.org/2001/XMLSchema#string>}
                ?region rdfs:label ?regionlabel
                }
                """)
    
    # query for all regions that have some sort of parent relationship and also finds the parent region
    parentsQuery = g.query(
               """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX fma: <http://purl.org/sig/ont/fma/>
                SELECT ?region ?parent
                WHERE { 
                ?region rdfs:subClassOf+ ?head.
                {?head fma:preferred_name "Segment of brain"^^<http://www.w3.org/2001/XMLSchema#string>}
                UNION {?head fma:preferred_name "Region of cerebral cortex"^^<http://www.w3.org/2001/XMLSchema#string>}
                ?region rdfs:subClassOf ?restrictionPar.
                {?restrictionPar owl:onProperty fma:regional_part_of}
                UNION  {?restrictionPar owl:onProperty fma:constitutional_part_of}
                ?restrictionPar owl:someValuesFrom ?parent.
                 }
                """)
      
    # query for all regions that have some sort of child relationship and also finds the child region
    childrenQuery = g.query(
                """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX fma: <http://purl.org/sig/ont/fma/>
                SELECT ?region ?child
                WHERE { 
                ?region rdfs:subClassOf+ ?head.
                {?head fma:preferred_name "Segment of brain"^^<http://www.w3.org/2001/XMLSchema#string>}
                UNION {?head fma:preferred_name "Region of cerebral cortex"^^<http://www.w3.org/2001/XMLSchema#string>}
                ?region rdfs:subClassOf ?restrictionChi.
                {?restrictionChi owl:onProperty fma:regional_part}
                UNION  {?restrictionChi owl:onProperty fma:constitutional_part}
                ?restrictionChi owl:someValuesFrom ?child.
                 }
                 """)
    
    # adding nodes to graph for all regions in 'regional part of brain' and includes their name
    for x in allQuery:
        node = str(x.region).lower()
        print 'all', node
        node_name = str(x.regionlabel).lower()
        netx.add_node(node, {'name':node_name})

    # adding edges for all pairs found from parentQuery
    for x in parentsQuery:
        print 'parents', node
        node = str(x.region).lower()
        parent = str(x.parent).lower()
        netx.add_edge(parent, node)    
    
    # adding edges for all pairs found from childQuery
    for x in childrenQuery:
        print 'children', node
        node = str(x.region).lower()
        child = str(x.child).lower()
        netx.add_edge(node, child)    
     
    with open(os.path.join(pklDir, pklFile),'wb') as output:
        pickle.dump(netx, output, -1)
    
t = storeFMAasGraph('/Users/jbwexler/Downloads/fma.owl', 'FMAgraph.pkl')



