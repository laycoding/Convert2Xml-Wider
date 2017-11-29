import os

gt_path = "./wider_face_val_v1.txt"
new_gt  = "./wider_face_val.txt"

result = open(new_gt, 'a')
with open(gt_path) as gt:
    annotations = gt.readlines()
num=len(annotations)
num_img = 0
for annotation in annotations:
    annotation = annotation.strip().split(' ')
    result.write(annotation[0].split('.')[0])
    result.write(' ')
    for i in xrange(len(annotation) - 2):
        result.write(annotation[i + 2])
        result.write(' ')
    result.write('\n')
result.close()

