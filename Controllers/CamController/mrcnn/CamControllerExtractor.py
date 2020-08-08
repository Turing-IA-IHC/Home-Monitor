import os
import sys
import random
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from cv2 import cv2
import warnings
warnings.filterwarnings("ignore")

# Import Mask RCNN
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
from mrcnn.coco import coco

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

class ObjectDetected():
    def __init__(self, className:str, frame, mask, backColor, y1, x1, y2, x2):
        self.ClassName:str=className
        self.Frame = frame
        self.Mask = mask
        self.backColor = backColor
        self.Y1 = y1
        self.X1 = x1
        self.Y2 = y2
        self.X2 = x2

class CamControllerExtractor:
    """ Allow detect people in an image """
    CLASSES_AVAILABLES = [
        'BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
        'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
        'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
        'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
        'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard',
        'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
        'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
        'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
        'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
        'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
        'teddy bear', 'hair drier', 'toothbrush'
    ]
    CLASSES_TO_DETECT = ['person']

    def __init__(self, cocoConfig=None, Me_Component_Path:str="./", coco_model_path=None):
        if cocoConfig == None:
            cocoConfig = InferenceConfig()
        if coco_model_path == None or coco_model_path == "":
            coco_model_path = "model/objectsModel.h5"
        coco_model_path = os.path.normpath(os.path.join(Me_Component_Path, coco_model_path))
            
        model_dir = os.path.join(Me_Component_Path, "logs")

        self.ME_MODEL = modellib.MaskRCNN(mode="inference", model_dir=model_dir, config=cocoConfig)
        self.ME_MODEL.load_weights(coco_model_path, by_name=True)

    def locatePeople(self, frame, backColor=[255,0,255]):
        """ Returns a image for each person in image.
            Moreover, returns square of person in image 
        """
        results = self.ME_MODEL.detect([frame], verbose=0)
        r = results[0]
        boxes, masks, ids, _ = r['rois'], r['masks'], r['class_ids'], r['scores']
        n_instances = boxes.shape[0]

        if not n_instances:
            print('NO INSTANCES TO DISPLAY')
            return []
        #else:
        #    assert boxes.shape[0] == masks.shape[-1] == ids.shape[0]

        Detections = []
        for i in range(n_instances):
            if not np.any(boxes[i]):
                continue

            if not self.CLASSES_AVAILABLES[ids[i]] in self.CLASSES_TO_DETECT: # Var OBJECTS in Config
                continue

            y1, x1, y2, x2 = boxes[i]
            mask = masks[:, :, i]
            image = frame.copy()

            for n in range(3): 
                image[:, :, n] = np.where(
                    mask == 0,
                    backColor[n],
                    image[:, :, n]
                )
            
            obj = ObjectDetected(self.CLASSES_AVAILABLES[ids[i]], image, mask, backColor, y1, x1, y2, x2)
            Detections.append(obj)

        return Detections    
