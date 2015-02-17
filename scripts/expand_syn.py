"""
takes string of keyword and returns list of strings of synonyms of the keyword
"""

import nibabel
import xml.etree.ElementTree as ET
import numpy
import os.path
import urllib2
from __builtin__ import True



def getSynonyms(keyword):
	keywordQuery = keyword
	keywordQuery = keywordQuery.replace(' ', '%20')
	keywordQuery = keywordQuery.replace('/', '')
	keywordQuery = keywordQuery.replace('\\', '')
	hdr = {'Accept': 'ext/html,application/xhtml+xml,application/xml,*/*'}
	target_url = 'http://nif-services.neuinfo.org/ontoquest/getprop/term/' + keywordQuery
	request = urllib2.Request(target_url,headers=hdr)
	synFile = urllib2.urlopen(request)		
	tree = ET.parse(synFile)
	root = tree.getroot()

	classes = root.findall('data/classes/class')
	syn_list = []
	for element in classes:
		synonyms = element.findall("properties/property[@name='has_exact_synonym']")
		for syn in synonyms:
			syn_list.append(syn.text)
	syn_list.append(keyword)
	return syn_list

