"""
takes string of keyword and returns list of strings of synonyms of the keyword
"""

import nibabel
import xml.etree.ElementTree as ET
import numpy
import os.path
import urllib2
from __builtin__ import True
import manual


def convertToList(filename):
    manualDir = manual.__path__[0]
    with open(os.path.join(manualDir, filename)) as fin:
        rows = [ line.split('\t') for line in fin ]
        d = { row[0]:row[1].replace('\n','') for row in rows[2:] }
    return d
	

def getSynonyms(keyword, remSyns = convertToList('rem_synonyms.txt'), addSyns = convertToList('add_synonyms.txt')):
	keywordQuery = keyword
	keywordQuery = keywordQuery.replace(' ', '%20')
	keywordQuery = keywordQuery.replace('/', '')
	keywordQuery = keywordQuery.replace('\\', '')
	hdr = {'Accept': 'ext/html,application/xhtml+xml,application/xml,*/*'}
	target_url = 'http://nif-services.neuinfo.org/ontoquest/getprop/term/' + keywordQuery
	for i in range(3):
		try:
			request = urllib2.Request(target_url,headers=hdr)
			synFile = urllib2.urlopen(request)	
		except:
			pass
		else:
			break
	else:
		return [keyword]
	tree = ET.parse(synFile)
	root = tree.getroot()

	classes = root.findall('data/classes/class')
	syn_list = []
	for element in classes:
		has_exact_synonyms = element.findall("properties/property[@name='has_exact_synonym']")
		has_related_synonym = element.findall("properties/property[@name='has_related_synonym']")
		synonym_ = element.findall("properties/property[@name='synonym']")
		synonyms = has_exact_synonyms + has_related_synonym + synonym_
		for syn in synonyms:
			#don't add synonyms if they are only numbers
			if not syn.text.isdigit():
				syn_list.append(syn.text.lower())
	syn_list.append(keyword.lower())
	syn_list_final = list(set(syn_list))
	
	# remove synonym relations from remSyns
	for syn1, syn2 in remSyns.items():
		if syn1 == keyword and syn2 in syn_list_final:
				syn_list_final.remove(syn2)
		elif syn2 == keyword and syn1 in syn_list_final:
			syn_list_final.remove(syn1)
			
	#add synonym relations from addSyns
	for syn1, syn2 in addSyns.items():
		if syn1 in syn_list_final and syn2 not in syn_list_final:
			syn_list_final.append(syn2)
		elif syn2 in syn_list_final and syn1 not in syn_list_final:
			syn_list_final.append(syn1)
		
	return syn_list_final
