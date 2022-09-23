import json

with open('JWL.json', 'r') as file:
    data = json.load(file)
    print(data)
    print(data['light'])