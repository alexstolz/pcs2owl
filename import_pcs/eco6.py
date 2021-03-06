#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
eco6.py

eCl@ss 6.X import module

Created by Alex Stolz on 2011-04-06.
Copyright (c) 2011 E-Business and Web Science Research Group. All rights reserved.
"""
import codecs
import csv

from util import * # imports also config, classes, rdflib, ...
import util

def importData():
	"""Loading facility"""
	print "Step 1: Loading PCS from %s" % __name__
	
	# ONTOLOGY: def __init__(self, title="", label="", description="", creator="", contributor="", rights="", subject="", license="", version="", seeAlso=""):
	util.metadata = Ontology("eClass 6.0", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger", version="1.0")
	
	# class synonyms
	names = {}
	print "loading class synonyms"
	synonym_de = csv.reader(open("pcs/eco6/eClass6_1_KW_de.csv", "r"), delimiter=";")
	for line in list(synonym_de)[1:]:
		idcl = line[3]
		desc = line[5]
		if not idcl in names:
			names[idcl] = []
		names[idcl].append(desc)
	
	codes = {}
	print "loading classes"
	artclass = csv.reader(open("pcs/eco6/eClass6_1_CC_de.csv", "r"), delimiter=";")
	for line in list(artclass)[1:]:
		# CLASS: def __init__(self, parent_id, class_id, label="", description=""):
		idcl = line[1]
		code = line[6]
		desc = line[7]
		codes[code] = idcl # append idcl with key of coded name
		if not idcl in names:
			names[idcl] = []
		names[idcl].append(desc)
		for k in range(0, len(code), 2):
			check = "00"
			if k == 0: # :-k with 0 would be understood incorrectly
				check = code[-2:]
			else:
				check = code[:-k][-2:]
			#print "len", len(code), "k", k, "test", check
			if check != "00":
				parent = code[:-k-2]+"0"*(k+2)
				if parent in codes:
					#print "%s (%s) is parent of %s (%s)" %(parent, codes[parent], code, codes[code])
					break
		code = codes[code]
		if parent == "00000000":
			parent = None
		else:
			parent = codes[parent]
		cappend(Class(parent, code, desc, desc, synonyms={"de":names[idcl]}))
	
	# feature
	# PROPERTY: def __init__(self, class_id, prop_id, label="", description="", prop_type=["qualitative", "string"]):
	feature2classes = {}
	print "loading feature2classes mapping"
	class2featuremap = csv.reader(open("pcs/eco6/eClass6_1_CC_PR_de.csv", "r"), delimiter=";")
	for line in list(class2featuremap)[1:]:
		idcl = line[1]
		idatt = line[4]
		if idatt not in feature2classes:
			feature2classes[idatt] = []
		feature2classes[idatt].append(idcl)
	
	feature2type = {}
	print "loading features"
	feature = csv.reader(open("pcs/eco6/eClass6_1_PR_de.csv", "r"), delimiter=";")
	for line in list(feature)[1:]:
		idatt = line[1]
		domain = []
		if idatt in feature2classes:
			domain = feature2classes[idatt]
		label = line[6]
		description = line[8]
		format = line[14]
		symbol = line[15] # e.g. mm for millimetres
		uom = line[16] # e.g. MMT for millimetres
		attribute_type = line[20] # e.g. direct (es erfolgt ein freier Eintrag) or indirect (Werte sind vorhanden)
		valency = line[21] # e.g. univalent (es wird genau ein Wert zugeordnet) or multivalent (Werte unbestimmter Anzahl werden zugeordnet)
		
		datatype = "string"
		object_type = "datatype"
		# http://www.heppnetz.de/projects/eclassowl/#gentax-properties
		if attribute_type == "indirect":
			object_type = "qualitative"
		elif format:
			if format[0] == "V": # boolean value
				object_type = "datatype"
				datatype = "boolean"
			elif "NR2" in format or "NE3" in format: # rational or exponential
				object_type = "quantitative"
				datatype = "float"
			elif "NR1" in format: # decimal
				object_type = "quantitative" # NR1 case has to be mapped manually, e.g. 10 properties ca. are datatype properties
				datatype = "integer"
			
		feature2type[idatt] = {}
		feature2type[idatt]["object_type"] = object_type
		feature2type[idatt]["datatype"] = datatype
		if len(domain) > 0:
			for d in domain:
				pappend(Property(d, idatt, label, description, prop_type=[object_type, datatype]))
		else:
			#print "could not determine domain for property", idatt, "- domain:", domain
			pappend(Property(None, idatt, label, description, prop_type=[object_type, datatype]))
		
	value2features = {}
	print "loading features2value mapping"
	feature2valuemap = csv.reader(open("pcs/eco6/eClass6_1_PR_VA_de.csv", "r"), delimiter=";")
	for line in list(feature2valuemap)[1:]:
		idatt = line[1]
		idvl = line[3]
		if idvl not in value2features:
			value2features[idvl] = []
		value2features[idvl].append(idatt)
		
	# INDIVIDUAL: def __init__(self, prop_id, inst_id, label="", description="", inst_type=""):
	print "loading values"
	value = csv.reader(open("pcs/eco6/eClass6_1_VA_de.csv", "r"), delimiter=";")
	for line in list(value)[1:]:
		idvl = line[1]
		label = line[6]
		description = line[7]
		if line[8]:
			description = line[8]
		if idvl in value2features:
			for feature in value2features[idvl]:
				if feature in feature2type:
					iappend(Individual(feature, idvl, label, description, [feature2type[feature]["object_type"], feature2type[feature]["datatype"]]))
				else:
					iappend(Individual(feature, idvl, label, description))


def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)