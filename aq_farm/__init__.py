from imageai.Detection import ObjectDetection
import os

execution_path = os.getcwd()

detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath(os.path.join(execution_path, "resnet50_coco_best_v2.1.0.h5"))
detector.loadModel()

detections = detector.detectObjectsFromImage(
    os.path.join(execution_path , "image.jpg"), os.path.join(execution_path , "imagenew.jpg")
)

for eachObject in detections:
    print(eachObject["name"] , " : " , eachObject["percentage_probability"] )