import json
import boto3

def lambda_handler(event, context):
    blob = event['Records'][0]['Sns']['Message']
    client = boto3.client('firehose')

    response = client.put_record(
    DeliveryStreamName='tweetindex',
    Record = {
            'Data': blob
            }
    )