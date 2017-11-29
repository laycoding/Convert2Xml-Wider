import os

gt_path = "./wider_face_val_bbx_gt.txt"
new_gt  = "./wider_face_val.txt"

result = open(new_gt, 'a')
with open(gt_path) as gt:
    annotations = gt.readlines()
num=len(annotations)
num_img = 0
counter = 2
for annotation in annotations:
    if annotation[-2] != ' ':
        counter = counter + 1
    
    if counter == 3:
        counter = 1
        result.write('\n')
        result.write(annotation[:-1])
        result.write(' ') #name
    elif counter == 2:
        result.write(annotation[:-14])
        result.write(' ')

result.close()

