"""
loads nif ontology from .pkl file and searches each term into PubMed [Title/Abstract]. adds the number of results
from each search and prints the total

initial total: 1092275
"""

import cPickle as pickle
import networkx as nx
from Bio import Entrez
from Bio.Entrez import efetch, read



with open('NIFgraph.pkl','rb') as input:
    nif = pickle.load(input)

Entrez.email='poldrack@stanford.edu'

total_results = 0

for node in nif:
    region = nif.node[node]['name']
    print region
    query = '"' + region + '"[tiab]'
    handle=Entrez.esearch(db='pubmed',term=query,retmax=100000)
    record = Entrez.read(handle)
    total_results += len(record['IdList'])
    print total_results

        
print 'total # of results: %d' %total_results