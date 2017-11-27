import boto3
import geocoder
from geocoder import location
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream
import time
import json

class listener(StreamListener):
    def on_data(self, raw_data):
        print(raw_data)
        all_data = json.loads(raw_data)
        loc_en = all_data["user"]["geo_enabled"]
        lang = all_data["user"]["lang"]

        if 'text' in all_data and loc_en and lang == "en":
            tweets = all_data["retweeted_status"]["text"]

            username = all_data["user"]["screen_name"]
            location = all_data["user"]["location"]

            response = q.send_message(MessageBody=tweets,
                                      MessageAttributes={
                                          'language': {
                                              'DataType': 'String',
                                              'StringValue': lang
                                          },
                                          'location': {
                                              'DataType': 'Number',
                                              'StringValue': location
                                          },
                                      })

        sqs = boto3.resource('sqs', region_name="us-west-2")
        q = sqs.get_queue_by_name(QueueName='tweets')

    def on_error(self, status_code):
        print (status_code)

def lambda_handler(event, context):
    c_key = "IwYigYDDZvsCNtncxP089dZ2Z"
    c_secret = "nORYTzVsrZx0EbNbuoasPw2DebpFeDan0gVFXjqF1rEF214Ztf"
    a_token = "919337290991919105-7x1YyFlW1zMlesToCHz6PtslIiwGxtF"
    a_secret = "ZmAKXHt5GgUzVNT9DXgaCKVuwbn7oNdRaF93YS5Vkh8Kj"
    auth = OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_token, a_secret)
    api = tweepy.API(auth)
    runtime = 40  
    twitterStream = Stream(auth, listener())        
    terms = ['Google','love','hate','story','work','life','haha','why','universe','now']
    twitterStream.filter(track=terms)
    time.sleep(runtime)
    twitterStream.disconnect()
