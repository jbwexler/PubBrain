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

def storeNIFAsGraph(owlPath = 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GrossAnatomy.owl', pklFile = 'NIFgraph.pkl', pklDir = ''):
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
                PREFIX ro: <http://www.obofoundry.org/ro/ro.owl#>
                PREFIX ont: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GrossAnatomy.owl#>
                SELECT (str(?label) as ?stringlabel)  (str(?region) as ?stringregion) 
                WHERE { 
                ?region rdfs:subClassOf+ ont:birnlex_1167.
                ?region rdfs:label ?label.
                 }
                """)
    
    # query for all regions that have some sort of parent relationship and also finds the parent region
    parentsQuery = g.query(
               """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX ro: <http://www.obofoundry.org/ro/ro.owl#>
                PREFIX ont: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GrossAnatomy.owl#>
                SELECT (str(?label) as ?stringlabel) (str(?region) as ?stringregion) (str(?parent) as ?stringparent) 
                WHERE { 
                ?region rdfs:subClassOf+ ont:birnlex_1167.
                ?region rdfs:label ?label.
               
                ?region rdfs:subClassOf ?restrictionPar.
                {?restrictionPar owl:onProperty ro:proper_part_of}
                UNION  {?restrictionPar owl:onProperty ro:located_in}
                UNION  {?restrictionPar owl:onProperty ro:contained_in}
                UNION  {?restrictionPar owl:onProperty ro:integral_part_of}
                ?restrictionPar owl:someValuesFrom ?parent.
                ?parent rdfs:subClassOf+ ont:birnlex_1167.
                 }
                """)
    
    # query for all regions that have some sort of child relationship and also finds the child region
    childrenQuery = g.query(
                """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX ro: <http://www.obofoundry.org/ro/ro.owl#>
                PREFIX ont: <http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-GrossAnatomy.owl#>
                SELECT (str(?label) as ?stringlabel)  (str(?region) as ?stringregion) (str(?child) as ?stringchild) 
                WHERE { 
                ?region rdfs:subClassOf+ ont:birnlex_1167.
                ?region rdfs:label ?label.
                ?region rdfs:subClassOf ?restrictionChi.
                {?restrictionChi owl:onProperty ro:has_integral_part}
                UNION  {?restrictionChi owl:onProperty ro:has_part}
                UNION  {?restrictionChi owl:onProperty ro:has_proper_part}
                ?restrictionChi owl:someValuesFrom ?child.
                ?child rdfs:subClassOf+ ont:birnlex_1167.
                 }
                 """)
    
    # adding nodes to graph for all regions in 'regional part of brain' and includes their name
    for x in allQuery:
        node = str(x.stringregion).lower()
        print node
        node_name = str(x.stringlabel).lower()
        netx.add_node(node, {'name':node_name})
    
    # adding edges for all pairs found from parentQuery
    for x in parentsQuery:
        node = str(x.stringregion).lower()
        parent = str(x.stringparent).lower()
        netx.add_edge(parent, node)    
    
    # adding edges for all pairs found from childQuery
    for x in childrenQuery:
        node = str(x.stringregion).lower()
        child = str(x.stringchild).lower()
        netx.add_edge(node, child)    
     
    with open(os.path.join(pklDir, pklFile),'wb') as output:
        pickle.dump(netx, output, -1)
        
def storeUberonAsGraph(owlPath = 'http://berkeleybop.org/ontologies/uberon.owl', pklFile = 'uberongraph.pkl', pklDir = ''):
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
                PREFIX ro: <http://www.obofoundry.org/ro/ro.owl#>
                PREFIX ont: <http://purl.obolibrary.org/obo/>
                SELECT (str(?label) as ?stringlabel)  (str(?region) as ?stringregion) 
                WHERE { 
                ?region rdfs:subClassOf+ ont:UBERON_0002616.
                ?region rdfs:label ?label.
                 }
                """)
    
    # query for all regions that have some sort of parent relationship and also finds the parent region
    parentsQuery = g.query(
               """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX ro: <http://www.obofoundry.org/ro/ro.owl#>
                PREFIX ont: <http://purl.obolibrary.org/obo/>
                SELECT (str(?label) as ?stringlabel) (str(?region) as ?stringregion) (str(?parent) as ?stringparent) (str(?parlabel) as ?stringparlabel)
                WHERE { 
                ?region rdfs:subClassOf+ ont:UBERON_0002616.
                ?region rdfs:label ?label.
                ?region rdfs:subClassOf ?restrictionPar.
                ?restrictionPar owl:onProperty ont:BFO_0000050.
                ?restrictionPar owl:someValuesFrom ?parent.
                ?parent rdfs:label ?parlabel
                 }
                """)
    
    
    # adding nodes to graph for all regions in 'regional part of brain' and includes their name
    for x in allQuery:
        node = str(x.stringregion).lower()
        print node
        node_name = str(x.stringlabel).lower()
        netx.add_node(node, {'name':node_name})
    
    # adding edges for all pairs found from parentQuery
    for x in parentsQuery:
        node = str(x.stringregion).lower()
        parent = str(x.stringparent).lower()
        parent_name = str(x.stringparlabel).lower()
        try:
            if not [n for n in netx if netx.node[n]['name'] == parent_name]:
                netx.add_node(parent, {'name':parent_name})
        except:
            netx.add_node(parent, {'name':parent_name})
        netx.add_edge(parent, node)    
    
     
    with open(os.path.join(pklDir, pklFile),'wb') as output:
        pickle.dump(netx, output, -1)
    
    

def storeFMAasGraph(owlPath = '/Users/jbwexler/Downloads/fma.owl', pklFile = 'FMAgraph.pkl', pklDir = ''):
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
                SELECT ?region ?parent ?parentlabel
                WHERE { 
                ?region rdfs:subClassOf+ ?head.
                {?head fma:preferred_name "Segment of brain"^^<http://www.w3.org/2001/XMLSchema#string>}
                UNION {?head fma:preferred_name "Region of cerebral cortex"^^<http://www.w3.org/2001/XMLSchema#string>}
                ?region rdfs:subClassOf ?restrictionPar.
                {?restrictionPar owl:onProperty fma:regional_part_of}
                UNION  {?restrictionPar owl:onProperty fma:constitutional_part_of}
                ?restrictionPar owl:someValuesFrom ?parent.
                ?parent rdfs:label ?parentlabel.
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
                SELECT ?region ?child ?childlabel
                WHERE { 
                ?region rdfs:subClassOf+ ?head.
                {?head fma:preferred_name "Segment of brain"^^<http://www.w3.org/2001/XMLSchema#string>}
                UNION {?head fma:preferred_name "Region of cerebral cortex"^^<http://www.w3.org/2001/XMLSchema#string>}
                ?region rdfs:subClassOf ?restrictionChi.
                {?restrictionChi owl:onProperty fma:regional_part}
                UNION  {?restrictionChi owl:onProperty fma:constitutional_part}
                ?restrictionChi owl:someValuesFrom ?child.
                ?child rdfs:label ?childlabel.
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
        parent_name = str(x.parentlabel).lower()
        try:
            if not [n for n in netx if netx.node[n]['name'] == parent_name]:
                netx.add_node(parent, {'name':parent_name})
        except:
            netx.add_node(parent, {'name':parent_name})
        netx.add_edge(parent, node)    
    
    # adding edges for all pairs found from childQuery
    for x in childrenQuery:
        print 'children', node
        node = str(x.region).lower()
        child = str(x.child).lower()
        child_name = str(x.childlabel).lower()
        try:
            if not [n for n in netx if netx.node[n]['name'] == child_name]:
                netx.add_node(child, {'name':child_name})
        except:
            netx.add_node(child, {'name':child_name})
        netx.add_edge(node, child)    
     
    with open(os.path.join(pklDir, pklFile),'wb') as output:
        pickle.dump(netx, output, -1)


# storeUberonAsGraph()
storeFMAasGraph()
