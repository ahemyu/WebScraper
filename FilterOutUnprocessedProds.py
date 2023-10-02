import json
import os
# Change working directory
os.chdir('C:/Users/GoekcekE/Desktop/repo/WebScrapper/jsons/Drive_Series')

# # Step 1: Read the JSON file with processed product name endings
# with open("have_spec_already.json", "r") as f:
#     processed_endings = json.load(f)

# # Step 2: Read the JSON file with complete product URLs
# with open("All_Controller_Prod_URLs.json", "r") as f:
#     all_product_links = json.load(f)




# # Step 3: Check each URL and filter out processed ones
# unprocessed_links = []
# for link in all_product_links:
#     print(link)
#     if not any(link.endswith(ending) for ending in processed_endings):
#         unprocessed_links.append(link)

# # Step 4: Save the list of unprocessed links to a new JSON file
# with open("Remaining_Prods_In_Controller_Series.json", "w") as f:
#     json.dump(unprocessed_links, f, indent=4)


# Step 1: Read the JSON file with processed product name endings
with open("have_spec_already.json", "r") as f:
    processed_endings = json.load(f)

# Step 2: Read the JSON file with complete product URLs
with open("All_Prods_Driver_Series.json", "r") as f:
    all_product_links = json.load(f)

# Step 3: Iterate through processed products and remove corresponding links
for ending in processed_endings:
    all_product_links = [link for link in all_product_links if not link.endswith(ending)]

# Step 4: Save the modified list of unprocessed links to a new JSON file
with open("unprocessed_links.json", "w") as f:
    json.dump(all_product_links, f, indent=4)