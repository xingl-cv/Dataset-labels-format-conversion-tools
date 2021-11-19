# -*- coding:utf-8 -*-
# @Date  : 2021/11/19
# sample: python voc2yolo.py -i data -o data -c dog,person

import os
import os.path as osp
from glob import glob
import click
import xml.etree.ElementTree as ET


def parse_folder(root):
    folder = root.find('folder').text
    return folder

def parse_filename(root):
    filename = root.find('filename').text
    return filename

def parse_source(root):
    source = root.find('source')
    database = source.find('database').text
    annotation = source.find('annotation').text
    image = source.find('image').text
    flickrid = source.find('flickrid').text
    return database, annotation, image, flickrid

def parse_owner(root):
    owner = root.find('owner')
    flickrid = owner.find('flickrid').text
    name = owner.find('name').text
    return flickrid, name

def parse_size(root):
    size = root.find('size')
    width = int(size.find('width').text)
    height = int(size.find('height').text)
    depth = int(size.find('depth').text)
    return width, height, depth

def parse_segmented(root):
    segmented = root.find('segmented')
    if int(segmented.text) == 0:
        pass
    pass
    return 

def parse_obj(obj):
    name = obj.find('name').text
    pose = obj.find('pose').text
    truncated = obj.find('truncated').text
    difficult = obj.find('difficult').text
    bndbox = obj.find('bndbox')
    xmin = int(bndbox.find('xmin').text)
    ymin = int(bndbox.find('ymin').text)
    xmax = int(bndbox.find('xmax').text)
    ymax = int(bndbox.find('ymax').text)
    return name, pose, truncated, difficult, xmin, ymin, xmax, ymax

def parse_object(root):
    object = root.iter('object')
    object_list = []
    for obj in object:
        name, pose, truncated, difficult, xmin, ymin, xmax, ymax = parse_obj(obj)
        object_list.append([name, pose, truncated, difficult, xmin, ymin, xmax, ymax])
    return object_list

def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    filename = parse_filename(root)
    width, height, _ = parse_size(root)
    object_list = parse_object(root)
    return filename, width, height, object_list

def convert_bbox(width, height, xmin, ymin, xmax, ymax):
    x = (xmin + xmax)/2.0
    y = (ymin + ymax)/2.0
    w = xmax - xmin
    h = ymax - ymin

    dw = 1./width
    dh = 1./height
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return x,y,w,h

def convert_file(xml_path, save_dir, classes):
    img_name, width, height, object_list = parse_xml(xml_path)
    txt_name = osp.splitext(img_name)[0]+'.txt'
    print(img_name, txt_name)

    os.makedirs(save_dir, exist_ok=True)
    with open(f'{osp.join(save_dir, txt_name)}', 'w') as f:
        for obj in object_list:
            [cls, _, _, _, xmin, ymin, xmax, ymax] = obj
            try:
                id = classes.index(cls)
                x,y,w,h = convert_bbox(width, height, xmin, ymin, xmax, ymax)
                f.write(f'{id} {x:6f} {y:6f} {w:6f} {h:6f}\n')
            except:
                print(f'{cls} is not in {classes}!')

@click.command()
@click.option('--input_dir','-i',required=True,type=str,help='VOC(.xml)文件所在文件夹')
@click.option('--output_dir','-o',required=True,type=str,help='YOLO(.txt)文件保存的文件夹')
@click.option('--classes','-c',required=True,type=str,help='需要转格式的标注的类别')
def main(input_dir, output_dir, classes):
    classes = classes.split(',')
    xml_path_list = glob(osp.join(input_dir, '*.xml'))
    for xml_path in xml_path_list:
        convert_file(xml_path, output_dir, classes)
    print('Convert VOC(.xml) to YOLO(.txt) done.')


if __name__ == "__main__":
    main()

