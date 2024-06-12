import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource and SNS client
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
table = dynamodb.Table('pixtag_db')  # Replace with your actual DynamoDB table name
sns_topic_arn = 'arn:aws:sns:us-east-1:025296372021:PixTag_Notifications'  # Replace with your actual SNS topic ARN

def lambda_handler(event, context):
    urls = event.get('url', [])
    action_type = event.get('type', 1)  # 1 for add, 0 for remove
    tags = event.get('tags', [])
    
    if not urls or not isinstance(action_type, int) or not tags:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid request format')
        }

    update_messages = []

    for url in urls:
        image_id = url.split('/')[-1].split('-thumb.png')[0]
        
        response = table.get_item(Key={'ImageID': image_id})
        if 'Item' not in response:
            continue
        
        item = response['Item']
        item['Labels'] = item.get('Labels', {})

        for tag in tags:
            if action_type == 1:  # Add tag
                if tag in item['Labels']:
                    item['Labels'][tag] += 1
                else:
                    item['Labels'][tag] = 1
                update_messages.append(f"Added tag '{tag}' to {url} (Image ID: {image_id})")
            elif action_type == 0:  # Remove tag
                if tag in item['Labels']:
                    item['Labels'][tag] -= 1
                    if item['Labels'][tag] <= 0:
                        del item['Labels'][tag]
                    update_messages.append(f"Removed tag '{tag}' from {url} (Image ID: {image_id})")

        table.put_item(Item=item)

    # Publish update message to SNS
    if update_messages:
        message = "\n".join(update_messages)
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject='Tag Updates Notification'
        )

    return {
        'statusCode': 200,
        'body': json.dumps('Tags updated successfully')
    }
