
# Importing required libraries
import json
import os
import shutil

os.chdir("C:\\Users\\GoekcekE\\Desktop\\repo\\WebScrapper\\jsons\\Hmi_Series")
# Create a 'faulty' folder if it doesn't exist
faulty_folder = 'faulty'
if not os.path.exists(faulty_folder):
    os.makedirs(faulty_folder)

# Iterate through each JSON file in the directory
for filename in os.listdir('.'):
    if filename.endswith('.json'):
        # Load the JSON file
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Check if 'documents' key exists and is an empty list
        if 'documents' in data and not data['documents']:
            # Move the file to the 'faulty' folder
            shutil.move(filename, os.path.join(faulty_folder, filename))
