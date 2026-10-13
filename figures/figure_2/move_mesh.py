import csv

with open('test.csv', newline='') as f:
    reader = csv.reader(f)
    meshes = list(reader)

meshes = meshes[0]
print(meshes)
