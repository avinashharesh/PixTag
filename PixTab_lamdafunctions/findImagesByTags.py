import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('pixtag_db')  # Replace 'pixtag_db' with your actual DynamoDB table name

def lambda_handler(event, context):
    # Parse the input tags from the event
    input_tags = event.get("tags", [])
    
    # Validate input
    if not input_tags:
        return {
            'statusCode': 400,
            'body': json.dumps('Tags are required')
        }
    
    # Build filter expression
    filter_expression = None
    for tag in input_tags:
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
