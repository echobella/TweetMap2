import boto3
import geocoder
from geocoder import location
# from tweepy import OAuthHandler
# from tweepy.streaming import StreamListener
# from tweepy import Stream
import tweepy
import time
import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
      if status.retweeted or status.lang != 'en'  or status.place is None :
            return
      text = status.text
      coords = (status.place.bounding_box.coordinates[0][0])
      # print('coords: ' + str(coords))
      created = status.created_at
      lang = status.lang

      pattern = '%Y-%m-%d %H:%M:%S'
      String_crea = str(created)

      blob = dict(
              text=text,
              coords=coords,
              created=str(created),
              lang=lang,
              timestamp = int(time.mktime(time.strptime(String_crea, pattern)))
            )
      blob = json.dumps(blob)

      sqs = boto3.client('sqs')
      queue_url = 'https://sqs.us-west-2.amazonaws.com/162672707961/tweets'
      
      response = sqs.send_message(QueueUrl=queue_url,MessageBody=(blob))
                                    # DelaySeconds=10
                                      
                                      # MessageAttributes={
                                      #     'language': {
                                      #         'DataType': 'String',
                                      #         'StringValue': lang
                                      #     },
                                      #     'location': {
                                      #         'DataType': 'Number',
                                      #         'StringValue': location
                                      #     },
                                      # }

        # sqs = boto3.resource('sqs', region_name="us-west-2")
        # q = sqs.get_queue_by_name(QueueName='tweets')

    def on_error(self, status_code):
        print (status_code)

def lambda_handler(event, context):
    c_key = ""
    c_secret = ""
    a_token = ""
    a_secret = ""
    auth = tweepy.OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_token, a_secret)
    api = tweepy.API(auth)
    stream_listener = StreamListener() # create an instance of StreamListener class
    runtime = 30
    Stream = tweepy.Stream(auth=api.auth, listener=stream_listener) # create an instance of the tweepy stream class, which will stream tweets        
    terms = ['Google','love','hate','story','work','life','haha','why','universe','now']
    Stream.filter(track=terms, async=True)
    time.sleep(runtime)
    Stream.disconnect()

    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-west-2.amazonaws.com/162672707961/tweets'

    t_end = time.time() + 40

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
              # print(message)

              rawTweet = json.loads(message['Body'])

              # print rawTweet["text"]
              # print rawTweet["lang"]

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
              username = "",
              password = "",
              version = "2017-02-27")

              try:
                  text= rawTweet["text"]
                  # print text
                  response = natural_language_understanding.analyze(
                  text= rawTweet["text"],
                  features= Features(sentiment=SentimentOptions())
                  )

                  # print response
                  # print type(response)
                  score = response["sentiment"]["document"]["score"]
                  label = response["sentiment"]["document"]["label"]

                  rawTweet['score'] = score
                  rawTweet['label'] = label
                  # print "score:" + score

                  receipt_handle = message['ReceiptHandle']

                  # Delete received message from queue
                  sqs.delete_message(
                      QueueUrl=queue_url,
                      ReceiptHandle=receipt_handle
                  )

                  sns = boto3.client('sns')
                  sns.publish(
                  TopicArn='arn:aws:sns:us-west-2:162672707961:tweet-lambda',
                  Message= json.dumps(rawTweet),
                  MessageStructure='string',
                  # Subject='ekrflr'
                  )
                  print "SNS Published"

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
