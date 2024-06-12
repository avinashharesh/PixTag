import json
import boto3
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pixtag_db')

    # Parse the incoming request
    thumbnail_url = event.get('thumbnail_url', '')

    # Query the table for the given thumbnail URL
    response = table.scan(
        FilterExpression=Attr('ThumbnailURL').eq(thumbnail_url)
    )

    # Check if the item is found
    if 'Items' in response and response['Items']:
        image_url = response['Items'][0]['SourceURL']
        return {
            'statusCode': 200,
            'body': json.dumps({'source_url': image_url})
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Thumbnail not found'})
        }
