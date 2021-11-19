# VOC-->YOLO
python voc2yolo.py -i data/voc/labels -o data/voc/yolo_labels -c dog,person
# YOLO-->VOC
python yolo2voc.py -i data/yolo/labels -o ./data/yolo/voc_lables -c dog,person
