import csv
import os
from os import system as shell

with open('test.csv', newline='') as f:
    reader = csv.reader(f)
    meshes = list(reader)

meshes = meshes[0]
print(meshes)

# need to write script to get those meshes and copy/paste 

mesh_path = '/home/hspillai/morphology_2d_1d/cylinderical/hemisphere/realL/Heatmap_4/meshes/'

for m in meshes:
    shell(f'cp -r {mesh_path}/{m} /home/hspillai/2d_1d_morphology/meshes/')
