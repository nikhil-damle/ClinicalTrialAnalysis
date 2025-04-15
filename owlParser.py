#!/usr/bin/env python
# coding: utf-8

# Author: Dr. Nikhil Damle<br>
# Company: PharmaLex GmbH<br>
# Date created: Mar 2025<br>
# Last Modified: 15 Apr 2025<br>
# Latest Modifications: Added comments to code<br>
# <br>
# ##### Latest updated version of the NCI-Thesaurus file used in this code (07th Apr 2025) was downloaded from https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/Thesaurus.OWL.zip 

# #### Import Libraries

get_ipython().run_cell_magic('time', '', 'import pandas as pd\nimport zipfile\nimport rdflib\nimport sys\n')


# #### Read the Thesaurus.owl file

get_ipython().run_cell_magic('time', '', "archive = zipfile.ZipFile('Thesaurus.OWL.zip', 'r')\nfile = archive.read('Thesaurus.owl')\n")


# #### Create a graph object and namespace 

get_ipython().run_cell_magic('time', '', "g = rdflib.Graph()\ng.parse (file, format='xml')\nncit = rdflib.Namespace('http://purl.obolibrary.org/obo/ncit.owl')\ng.bind('ncit', ncit)\n")


# #### Execute q SPARQL query against the graph object

get_ipython().run_cell_magic('time', '', 'query = """\nprefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nprefix owl: <http://www.w3.org/2002/07/owl#>\n \nSELECT distinct ?code ?prefName ?displayName (group_concat(distinct ?synonym; separator="; ") as ?synonyms)\nWHERE {\n?s rdf:type owl:Class ;\n    <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#NHC0> ?code ;\n    <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#P108> ?prefName ;\n    <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#P107> ?displayName ;\n    <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#P90> ?synonym .\n}\ngroup by ?code\n"""\n\nresult = g.query(query)\nprint(len(result))\n')


# #### Convert the SPARQL query results to DFrame and save a csv to avoid repeated graph-creation and query opertations

data = []
for row in result:
    data.append({str(var): str(row[var]) for var in row.labels})

# Convert the list of dictionaries to a DataFrame
dfNCIT = pd.DataFrame(data)

# Display the DataFrame
#print(dfNCIT)
dfNCIT.to_csv('ncit.csv', sep='\t', index=False, mode='a')