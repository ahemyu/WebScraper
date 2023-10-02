import os
import json

# Path to the directory containing the JSON files
# Setting it to '.' means the current directory
folder_path = "C:/Users/GoekcekE/Desktop/repo/WebScrapper/jsons/Drive_Series"

# List to store the names of the JSON files (excluding the .json extension)
json_names = []

# Traverse the folder to get all files
for filename in os.listdir(folder_path):
    # Check if the file is a JSON file
    if filename.endswith('.json'):
        # Remove the .json extension, convert to lowercase, and replace underscores with slashes
        modified_name = filename[:-5].lower().replace('_', '-') + ".html"
        json_names.append(modified_name)

# Serialize the list to a JSON file
with open("have_spec_already", "w") as f:
    json.dump(json_names, f, indent=4)

# Print the list to console so you can copy it, if needed
print(json.dumps(json_names, indent=4))