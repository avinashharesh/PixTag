import boto3
import cv2
import os
import json

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')  # Lambda client to invoke another function

def create_thumbnail(image_path, thumbnail_path):
    image = cv2.imread(image_path)
    thumbnail = cv2.resize(image, (128, 128))  # Resize to 128x128 pixels
    cv2.imwrite(thumbnail_path, thumbnail)

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    download_path = f'/tmp/{os.path.basename(key)}'
    thumbnail_path = f'/tmp/{os.path.basename(key)}'  # Ensure different name for thumbnail
    target_bucket = 'pixtag-thumbnails'

    # Download the image from S3
    s3.download_file(source_bucket, key, download_path)

    # Create the thumbnail
    create_thumbnail(download_path, thumbnail_path)

    # Define the thumbnail's key and the content type based on file extension
    thumbnail_key = f'{os.path.basename(key)}'
    content_type = 'image/jpeg'  # or 'image/png' based on your specific needs

    # Upload the thumbnail to the target S3 bucket under the 'thumbnails/' prefix with additional metadata
    s3.upload_file(
        thumbnail_path,
        target_bucket,
        thumbnail_key,
        ExtraArgs={
            'ContentType': content_type,
            'ContentDisposition': 'inline'  # This enables images to be displayed rather than downloaded
        }
    )

    # Payload for the second Lambda function
    payload = {
        'source_bucket': source_bucket,
        'original_image_key': key,
        'thumbnail_key': thumbnail_key,
        'target_bucket': target_bucket
    }

    # Invoke the second Lambda function on success
    response = lambda_client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:025296372021:function:object_detection',
        InvocationType='RequestResponse',  # Or use 'Event' if you do not need the response immediately
        Payload=json.dumps(payload)
    )

    # Extract the necessary part from the response, if needed
    response_payload = json.load(response['Payload'])

    return {
        'statusCode': 200,
        'body': {
            'message': 'Thumbnail created and uploaded successfully, second lambda invoked.',
            'original_image_key': key,
            'thumbnail_key': thumbnail_key,
            'lambda_response': response_payload  # Ensure this is serializable
        }
    }
