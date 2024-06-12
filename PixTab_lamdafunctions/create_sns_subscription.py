import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
    sns_client = boto3.client('sns', region_name='us-east-1')
    user_pool_id = 'us-east-1_MxdMYnssX'
    topic_arn = 'arn:aws:sns:us-east-1:025296372021:PixTag_Notifications'  # Replace with your Topic ARN

    try:
        # Retrieve users from Cognito
        response = cognito_client.list_users(UserPoolId=user_pool_id)
        email_addresses = [user['Attributes'][0]['Value'] for user in response['Users'] if user['Attributes'][0]['Name'] == 'email']

        # Retrieve current subscriptions to the topic
        existing_subscriptions = {}
        paginator = sns_client.get_paginator('list_subscriptions_by_topic')
        for page in paginator.paginate(TopicArn=topic_arn):
            for subscription in page['Subscriptions']:
                if subscription['Protocol'] == 'email':
                    existing_subscriptions[subscription['Endpoint']] = subscription['SubscriptionArn']

        subscription_arns = []
        for email in email_addresses:
            if email not in existing_subscriptions:
                # Subscribe each email to the SNS topic if not already subscribed
                subscribe_response = sns_client.subscribe(
                    TopicArn=topic_arn,
                    Protocol='email',
                    Endpoint=email
                )
                subscription_arns.append(subscribe_response['SubscriptionArn'])
            else:
                subscription_arns.append(existing_subscriptions[email])

        return {
            'statusCode': 200,
            'body': f'Subscriptions successful: {subscription_arns}'
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': f'An error occurred: {e.response["Error"]["Message"]}'
        }
