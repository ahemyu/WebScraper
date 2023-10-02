
####
# This script parses a JSON file that has been scrapped from the 
# e.g. https://emea.mitsubishielectric.com/fa/products/drv/servo/mr_j4/servo-amplifier/mr-j4-60b-rj.html
# and creates the submodel documentation according to the IDTA publication (Doc Number 2004, Version 1.2)
#
# Author: FA-EDC MM
#
####
import json
import pprint

#Globals
path_to_scrapped = "MR-J4-60B-RJ.json"
path_to_doc_tmpl = "DocumentVersion_TemplateV3.json"
path_to_sm_tmpl = "Submodel_HandoverDocumentationV3.json"


def create_document(data):
    #Read the template as string
    f = open(path_to_sm_tmpl)
    template_data = f.read();
    
     # Replace the palceholders

    #File Handling
    template_data = template_data.replace("[doc_extension]", data["doc_extension"])
    template_data = template_data.replace("[doc_link]", data["doc_link"])

    template_data = template_data.replace("[doc_language]", data["doc_language"])    
    template_data = template_data.replace("[doc_name]", data["doc_name"])
    template_data = template_data.replace("[doc_release_year]", data["doc_release_year"])
    template_data = template_data.replace("[doc_size]", data["doc_size"])
    template_data = template_data.replace("[doc_type]", data["doc_type"])
    template_data = template_data.replace("[doc_version]", data["doc_version"])

    #Expected Input Data looks like this:
    #{'doc_extension': 'PDF',
    #'doc_language': ['Deutsch'],        
    #'doc_link': '',
    #'doc_name': 'Einsteigerhandbuch '   
    #            'MR-J4-Servoverstärker',
    #'doc_release_year': '2018',
    #'doc_size': '8.4 MiB',
    #'doc_type': 'Handbücher',
    #'doc_version': 'B'}

    # Return the Submodel Element
    f.close()
    return json.loads(template_data)


# Read the JSON files resulted from the web scrapping
   
# Opening JSON file
f = open(path_to_scrapped)
   
# returns JSON object as 
# a dictionary
data = json.load(f)
#pprint.pprint(data)

# Read the Submodel Template JSON files. File contains the template for one document with several

# Create the Submodel Template Meta Data for Documentation (or read from a file and replace)

for p in data:
    print(p["product"])
    for s in p["series"]:
        print(s["product_name"] + " " + s["series_name"])
        for d in s["documents"]:
            sme_document = create_document(d)

f.close()