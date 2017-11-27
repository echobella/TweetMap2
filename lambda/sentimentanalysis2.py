import boto3
import settings
import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions
import time

def lambda_handler(event, context):

    # Create SQS client
    
    sqs = boto3.client('sqs')
    queue_url = settings.SQS_URL

    t_end = time.time() + 50

    while time.time() < t_end:
    # while True:
        # Receive message from SQS queue
        response = sqs.receive_message(
            QueueUrl=queue_url,
            VisibilityTimeout=10,
            WaitTimeSeconds=0
        )

        if 'Messages' not in response:
            return

        message = response['Messages'][0]

        rawTweet = json.loads(message['Body'])

        print 'Hello'
        print rawTweet["text"]
        print rawTweet["lang"]

        tweetText = rawTweet["text"]
        if len(tweetText) < 15:
            rawTweet['score'] = -99
            rawTweet['label'] = "LengthIsNotSufficient"

            receipt_handle = message['ReceiptHandle']
            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            continue

        natural_language_understanding = NaturalLanguageUnderstandingV1(
        username = "f9d857e5-39ef-432f-ac9a-4b4ff012132f",
        password = "1slUHK2HnxOD",
        version = "2017-02-27")

        try:
            response = natural_language_understanding.analyze(
            text= rawTweet["text"],
            features= Features(sentiment=SentimentOptions())
            )
            score = response["sentiment"]["document"]["score"]
            label = response["sentiment"]["document"]["label"]

            rawTweet['score'] = score
            rawTweet['label'] = label

            receipt_handle = message['ReceiptHandle']

            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )

            sns = boto3.client('sns')
            sns.publish(
            TopicArn='arn:aws:sns:us-east-1:672459173447:tweetStage',
            Message= json.dumps(rawTweet),
            Subject='yo',
            MessageStructure='string',
            )

        except:
            rawTweet['score'] = 400
            rawTweet['label'] = "WatsonAPIError"

            receipt_handle = message['ReceiptHandle']
            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            continue