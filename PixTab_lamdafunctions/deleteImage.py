import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Initialize clients
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pixtag_db')

    # S3 bucket names
    original_bucket = 'pixtag-original-images'
    thumbnail_bucket = 'pixtag-thumbnails'

    # Parse the incoming request
    urls = event.get('url', [])

    for url in urls:
        # Extract the image ID from the URL
        image_id = url.split('/')[-1]

        # Check if the original image exists in S3
        try:
            s3.head_object(Bucket=original_bucket, Key=image_id)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return {
                    'statusCode': 403,
                    'body': json.dumps({'message': 'image not found in original bucket'})
                }

        # Check if the thumbnail image exists in S3
        try:
            s3.head_object(Bucket=thumbnail_bucket, Key=image_id)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return {
                    'statusCode': 403,
                    'body': json.dumps({'message': 'image not found in thumbnail bucket'})
                }

        # Delete the original image from S3
        s3.delete_object(Bucket=original_bucket, Key=image_id)

        # Delete the thumbnail image from S3
        s3.delete_object(Bucket=thumbnail_bucket, Key=image_id)

        # Delete the item from DynamoDB
        table.delete_item(
            Key={'ImageID': image_id}
        )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Images and records deleted successfully'})
    }
