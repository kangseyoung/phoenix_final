import json
import os

path = '/home/rapa/phoenix_pipeline_folders/pipeline/launcher/loader/data_from_loader'
json_name = 'json_from_loader.json'
json_path = os.path.join(path,json_name)

dic = {'project_id' : 254,
       'user_id' : 90}

if not os.path.exists(path):
    os.makedirs(path)

with open(json_path, "w") as f:
    json.dump(dic, f, indent=4)
