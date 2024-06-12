import boto3
import json

# Initialize AWS clients
cognito_idp = boto3.client('cognito-idp')
sns = boto3.client('sns')

# SNS details
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:025296372021:PixTag_Notifications'  # Replace with your SNS topic ARN


def publish_message(topic_arn, message, subject):
    """Publish a message to an SNS topic."""
    response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject
    )
    return response

def lambda_handler(event, context):
    # Extract image URL and detected tags from the event
    image_url = event['image_url']
    detected_tags = event['detected_tags']

    # Construct the message
    message = f"Image URL: {image_url}\nDetected Tags: {', '.join(detected_tags)}"
    subject = "New Image Processed"

    # Publish the message to SNS
    response = publish_message(SNS_TOPIC_ARN, message, subject)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Email notifications sent successfully',
            'snsResponse': response
        })
    }
