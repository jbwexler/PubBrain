"""
maps each region in an ontology graph to its best matching region in the atlas (using toAtlas).
output is a dictionary with atlas regions as keys and list of corresponding ontology regions as values.
"""

import xml.etree.ElementTree as ET
import numpy
import os.path
from __builtin__ import True
import networkx as nx
import cPickle as pickle
from networkx import NetworkXError
from expand_syn import getSynonyms
from boto.s3.multipart import Part
import xlwt
from itertools import izip_longest
from pubbrain_app.models import BrainRegion


def findNodes(graph, startNode, synonymsDict, direction = 'children', printStuff = False, level = ''):
    level += '_'
    matches = [key for key in synonymsDict.keys() if graph.node[startNode]['name'] in synonymsDict[key]]
    if matches != []:
        return matches
    else:
        matchingRelatives = []
        if direction == 'parents':
            for parent in graph.predecessors_iter(startNode):
                if printStuff == True:
                    print level, graph.node[parent]['name']
                matchingRelatives += findNodes(graph, parent, synonymsDict, direction, printStuff, level)

        else:
            for child in graph.successors_iter(startNode):
                if printStuff == True:
                    print level, graph.node[child]['name']
                matchingRelatives += findNodes(graph, child, synonymsDict, direction, printStuff, level)
        return matchingRelatives


def toAtlas(graph, region, synonymsDict, parentChildren):
    final_list = []
    # checking if region or synonyms exist in atlas. if so, simply return region
    for atlasRegion in synonymsDict.keys():
        if region in synonymsDict[atlasRegion]:
            final_list.append(atlasRegion)   
    if final_list != [] or parentChildren == False: 
        return final_list
            
    if region in ['anterior commissure', 'internal capsule', 'middle temporal gyrus', 'area postrema', 'substantia nigra', 'hippocampus', 'vermis']:
        print
        print region
        printStuff = True
    else:
        printStuff = False
    # checking recursively for child matches
    region_id = [n for n,d in graph.nodes_iter(data=True) if d['name'] == region][0]   
    if printStuff == True:
        print 'children: '
    matchingChildren = findNodes(graph, region_id, synonymsDict, 'children', printStuff)
    # checking recursively for parent matches
    if printStuff == True:
        print 'parents: '
    matchingParents = findNodes(graph, region_id, synonymsDict, 'parents', printStuff)
    final_list = matchingChildren + matchingParents
    if printStuff == True:
        print final_list
    return final_list
        

def createMap(graph, atlas_dir = '/Applications/fmri_progs/fsl/data/atlases/', parentChildren = True):
    fullMap = {}
    atlasRegions = set()
    for file_name in os.listdir(atlas_dir):
        if '.xml' in file_name and file_name != 'Talairach.xml': 
            tree = ET.parse(os.path.join(atlas_dir, file_name))
            root = tree.getroot()
            for line in root.find('data').findall('label'):
                name = line.text.replace("'",'').rstrip(' ').lower()
                atlasRegions.add(name)
    
    synonymsDict = {}
    for region in atlasRegions:
        synonymsDict[region] = getSynonyms(region)
    for node in graph:
        nodeName = graph.node[node]['name']
        fullMap[nodeName] = toAtlas(graph, nodeName, synonymsDict, parentChildren)
    return fullMap


with open('NIFgraph.pkl','rb') as input:
    nif = pickle.load(input)
    
excel = xlwt.Workbook()
sheet1 = excel.add_sheet('sheet1')
justSyn = createMap(nif, parentChildren=False)
parChi = createMap(nif)
excelList = [[],[],[]]

# for atlasRegion in justSyn.keys():
#     sortedZip = izip_longest(justSyn[atlasRegion].sort(), parChi[atlasRegion].sort())
#     for (justRegion, parRegion) in sortedZip:
#         excelList[0].append(atlasRegion)
#         excelList[1].append(justRegion)
#         excelList[2].append(parRegion)
# for node in nif:
#     nodeName = nif.node[node]['name']
#     if nodeName .

        
count = 1
for ontRegion in parChi.keys():
    sortedZip = izip_longest(sorted(parChi.get(ontRegion)), sorted(justSyn.get(ontRegion)))
    for (parChiRegion, justSynRegion) in sortedZip:
        sheet1.write(count,1, ontRegion)
        sheet1.write(count,2, justSynRegion)
        sheet1.write(count,3, parChiRegion)
        sheet1.write(count,4, len(BrainRegion.objects.get(name=ontRegion).pmid_set.all()))
        count += 1
for node in nif:
    nodeName = nif.node[node]['name']
    if justSyn[nodeName] == [] and parChi[nodeName] == []:
        sheet1.write(count,1, nodeName)
        sheet1.write(count,4, len(BrainRegion.objects.get(name=nodeName).pmid_set.all()))
        count +=1
excel.save('/Users/jbwexler/poldrack_lab/cs/other/ontmapreverse.xls')  
print 'done'
    

