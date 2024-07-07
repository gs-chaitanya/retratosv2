import json

config = {"n": ['gender'], 
          "vblex": "value2"}

with open('config.json', 'w') as f:
    json.dump(config, f)