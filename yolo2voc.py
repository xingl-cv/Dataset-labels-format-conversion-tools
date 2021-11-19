# -*- coding:utf-8 -*-
# @Date  : 2021/11/19

'''
input dir format:
{cur_dir}/yolo/images/*.jpg
{cur_dir}/yolo/labels/*.txt

output dir format::
{cur_dir}/voc/images/*.jpg
{cur_dir}/voc/labels/*.xml
'''

'''
目前存在一个问题：VOC(.xml)转换到YOLO(.txt)后，因为精度转换的问题，
在由YOLO(.txt)转到VOC(.xml)时，某些点出现 1 像素的误差
'''

import os
import os.path as osp
from glob import glob
import click
# import xml.etree.ElementTree as ET
from lxml import etree
import cv2 as cv


def create_root():
    root = etree.Element('Annotation')
    return root

def create_folder(root, folder='VOC2017'):
    etree.SubElement(root, 'folder').text = str(folder)

def create_filename(root, img_name):
    etree.SubElement(root, 'filename').text = str(img_name)

def create_source(root, database='The VOC2007 Database', annotation='PASCAL VOC2007', image='flickr', flickrid='flickrid'):
    source = etree.SubElement(root, 'source')
    etree.SubElement(source, 'database').text = str(database)
    etree.SubElement(source, 'annotation').text = str(annotation)
    etree.SubElement(source, 'image').text = str(image)
    etree.SubElement(source, 'flickrid').text = str(flickrid)
    
def create_owner(root, flickrid='Fried Camels', name='Jinky the Fruit Bat'):
    owner = etree.SubElement(root, 'owner')
    etree.SubElement(owner, 'flickrid').text = str(flickrid)
    etree.SubElement(owner, 'name').text = str(name)

def create_size(root, width, height, depth):
    size = etree.SubElement(root, 'size')
    etree.SubElement(size, 'width').text = str(width)
    etree.SubElement(size, 'height').text = str(height)
    etree.SubElement(size, 'depth').text = str(depth)
    
def create_segmented(root):
    # 图像分割使用这个，暂时不支持
    etree.SubElement(root, 'segmented').text = 0


def create_bndbox(object, xmin, ymin, xmax, ymax):
    bndbox = etree.SubElement(object, 'object')
    etree.SubElement(bndbox, 'xmin').text = str(xmin)
    etree.SubElement(bndbox, 'ymin').text = str(ymin)
    etree.SubElement(bndbox, 'xmax').text = str(xmax)
    etree.SubElement(bndbox, 'ymax').text = str(ymax)

def create_object(root, name, xmin, ymin, xmax, ymax, pose='Left', truncated=1, difficult=0):
    object = etree.SubElement(root, 'object')
    etree.SubElement(object, 'name').text = str(name)
    etree.SubElement(object, 'pose').text = str(pose)
    etree.SubElement(object, 'truncated').text = str(truncated)
    etree.SubElement(object, 'difficult').text = str(difficult)
    create_bndbox(object, xmin, ymin, xmax, ymax)

def convert_bbox(dw, dh, x, y, w, h):
    # dw、dh 是图像的宽、高
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    xmin = int(x+1-w/2)
    ymin = int(y+1-h/2)
    xmax = int(x+1+w/2)
    ymax = int(y+1+h/2)
    return xmin,ymin,xmax,ymax

def parse_txt(txt_path):
    with open(txt_path, 'r') as f:
        contents = f.readlines()

    info_list = []
    for content in contents:
        content = content.strip('\n').split()
        id = int(content[0]) # cls
        x = float(content[1])
        y = float(content[2])
        w = float(content[3])
        h = float(content[4])
        info_list.append([id, x, y, w, h])
    return info_list

def convert_file(txt_path, save_dir, classes):
    img_path = txt_path.replace('labels','images').replace('.txt', '.jpg')
    img = cv.imread(img_path)
    height, width, depth = img.shape[0], img.shape[1], img.shape[2]

    img_name = osp.basename(img_path)
    root = create_root()
    create_folder(root, folder='VOC2017')
    create_filename(root, img_name)
    create_source(root)
    create_owner(root)
    create_size(root, width, height, depth)
    
    info_list = parse_txt(txt_path)
    for info in info_list:
        id, x, y, w, h = info
        name = classes[id]
        xmin, ymin, xmax, ymax = convert_bbox(width, height, x, y, w, h)
        create_object(root, name, xmin, ymin, xmax, ymax)

    tree = etree.ElementTree(root)
    xml_path = osp.join(save_dir, osp.basename(txt_path).replace('.txt', '.xml'))
    tree.write(xml_path, pretty_print=True, xml_declaration=False, encoding='utf-8')

@click.command()
@click.option('--input_dir','-i',required=True,type=str,help='YOLO(.txt)文件所在文件夹')
@click.option('--output_dir','-o',required=True,type=str,help='VOC(.xml)文件保存的文件夹')
@click.option('--classes','-c',required=True,type=str,help='需要转格式的标注的类别')
def main(input_dir, output_dir, classes):
    print(classes)
    classes = classes.split(',')
    txt_path_list = glob(osp.join(input_dir, '*.txt'))
    for txt_path in txt_path_list:
        convert_file(txt_path, output_dir, classes)
    print('Convert YOLO(.txt) to VOC(.xml) done.')


if __name__ == "__main__":
    main()