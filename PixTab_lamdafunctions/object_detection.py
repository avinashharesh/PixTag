import boto3
import cv2
import numpy as np
import os
import json

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')  # Lambda client to invoke another function

table = dynamodb.Table('pixtag_db')  # Your DynamoDB table name

# Paths to YOLO configuration files in S3
yolo_bucket = 'pixtag-python-dependencies'
config_key = 'yolov3-tiny.cfg'
weights_key = 'yolov3-tiny.weights'
labels_key = 'coco.names'

def download_yolo_files():
    config_path = f'/tmp/{os.path.basename(config_key)}'
    weights_path = f'/tmp/{os.path.basename(weights_key)}'
    labels_path = f'/tmp/{os.path.basename(labels_key)}'

    s3.download_file(yolo_bucket, config_key, config_path)
    s3.download_file(yolo_bucket, weights_key, weights_path)
    s3.download_file(yolo_bucket, labels_key, labels_path)

    return config_path, weights_path, labels_path

# Load YOLOv3 model
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
    predictions = []
    if len(idxs) > 0:
        for i in idxs.flatten():
            predictions.append({
                "label": LABELS[classIDs[i]],
                "accuracy": confidences[i],
                "rectangle": {
                    "left": boxes[i][0],
                    "top": boxes[i][1],
                    "width": boxes[i][2],
                    "height": boxes[i][3]
                }
            })
    else:
        return -1
    return predictions

def save_to_dynamodb(tags, source_url, thumbnail_url):
    label_counts = {}
    for tag in tags:
        label = tag['label']
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts[label] = 1

    response = table.put_item(
        Item={
            'ImageID': os.path.basename(source_url),
            'Labels': label_counts,
            'SourceURL': source_url,
            'ThumbnailURL': thumbnail_url
        }
    )
    return response

def invoke_send_email(image_url, detected_tags):
    payload = {
        "image_url": image_url,
        "detected_tags": detected_tags
    }
    response = lambda_client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:025296372021:function:send_email',
        InvocationType='Event',
        Payload=json.dumps(payload)
    )
    return response

def lambda_handler(event, context):
    thumbnail_bucket = event['target_bucket']
    source_bucket = event['source_bucket']
    original_image_key = event['original_image_key']
    thumbnail_key = event['thumbnail_key']

    original_image_path = f'/tmp/{os.path.basename(original_image_key)}'
    thumbnail_path = f'/tmp/thumbnail-{os.path.basename(thumbnail_key)}'

    s3.download_file(source_bucket, original_image_key, original_image_path)
    s3.download_file(thumbnail_bucket, thumbnail_key, thumbnail_path)

    config_path, weights_path, labels_path = download_yolo_files()

    image = cv2.imread(original_image_path)
    if image is None or image.size == 0:
        return {'statusCode': 404, 'message': 'Image is empty or not loaded correctly'}
    net, LABELS = load_yolo(config_path, weights_path, labels_path)

    predictions = do_prediction(image, net, LABELS)
    if not predictions or predictions == -1:
        return {'statusCode': 404, 'message': 'No predictions found'}

    source_url = f"https://{source_bucket}.s3.amazonaws.com/{original_image_key}"
    thumbnail_url = f"https://{thumbnail_bucket}.s3.amazonaws.com/{thumbnail_key}"

    # Save predictions to DynamoDB
    save_to_dynamodb(predictions, source_url, thumbnail_url)

    # Send email with image URL and detected tags
    invoke_send_email(source_url, [tag['label'] for tag in predictions])

    return {'statusCode': 200, 'body': predictions}
