import json
import boto3
import cv2
import numpy as np
from boto3.dynamodb.conditions import Key, Attr
import base64

# Initialize S3 and DynamoDB clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pixtag_db')  # Replace with your actual DynamoDB table name

# Paths to YOLO configuration files in S3
yolo_bucket = 'pixtag-python-dependencies'
config_key = 'yolov3-tiny.cfg'
weights_key = 'yolov3-tiny.weights'
labels_key = 'coco.names'

def download_yolo_files():
    config_path = f'/tmp/{config_key}'
    weights_path = f'/tmp/{weights_key}'
    labels_path = f'/tmp/{labels_key}'

    s3.download_file(yolo_bucket, config_key, config_path)
    s3.download_file(yolo_bucket, weights_key, weights_path)
    s3.download_file(yolo_bucket, labels_key, labels_path)

    return config_path, weights_path, labels_path

# Load YOLO model
def load_yolo(config_path, weights_path, labels_path):
    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    with open(labels_path, "r") as f:
        classes = f.read().strip().split('\n')
    return net, classes

def do_prediction(image, net, LABELS, confthres=0.3, nmsthres=0.2):
    (H, W) = image.shape[:2]
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)
    boxes = []
    confidences = []
    classIDs = []
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > confthres:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres, nmsthres)
    tags = []
    if len(idxs) > 0:
        for i in idxs.flatten():
            tags.append(LABELS[classIDs[i]])
    return tags

def lambda_handler(event, context):
    # Parse the image data from the event
    image_data = base64.b64decode(event['image'])
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Download YOLO files
    config_path, weights_path, labels_path = download_yolo_files()

    # Load YOLO model
    net, LABELS = load_yolo(config_path, weights_path, labels_path)
    
    # Get tags from the image
    tags = do_prediction(image, net, LABELS)
    
    if not tags:
        return {
            'statusCode': 404,
            'body': json.dumps('No tags found in the image')
        }

    # Build filter expression for DynamoDB query
    filter_expression = None
    for tag in tags:
        if filter_expression is None:
            filter_expression = Attr('Labels.' + tag).exists()
        else:
            filter_expression = filter_expression & Attr('Labels.' + tag).exists()

    # Scan DynamoDB table with filter expression
    response = table.scan(
        FilterExpression=filter_expression
    )

    # Collect the URLs of the images
    links = []
    for item in response.get('Items', []):
        links.append(item['ThumbnailURL'])

    return {
        'statusCode': 200,
        'body': json.dumps({"links": links})
    }
