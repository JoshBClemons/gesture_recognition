import tweepy
import time
import pandas as pd
pd.set_option('display.max_colwidth', 1000)

# api key
api_key = 'VDq2mD1Ia72tGNjwYNdZMfpsq'
# api secret key
api_secret_key = 'xMLNsTqX5Fh1HkSJSSxpzlODmoMt5GZrisFljwUQY98tZZA6GL'
# access token
access_token = '306435942-FWcbZ0ItTdmSTiZIiDkbLYkVUr8xD2QWHECk361j'
# access token secret
access_token_secret = 'pOollieBi8mvHBhbufNWvlrD8tC9RRXIE3bG3vtQpHwWk'
# bearer token 
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAMmTMAEAAAAA2JxGmB0SWspD70bll4cbkwxBtrU%3DyQwVvBrcpSF4GkQl0B5b90lcBdMn69fIS6aJ9onbctud7tXBj8'

authentication = tweepy.OAuthHandler(api_key, api_secret_key)
authentication.set_access_token(access_token, access_token_secret)
api = tweepy.API(authentication, wait_on_rate_limit=True)

def get_related_tweets(text_query):
    # list to store tweets
    tweets_list = []
    # no of tweets
    count = 1
    try:
        # Pulling individual tweets from query
        for tweet in api.search(q=text_query, count=count):
            print(tweet.text)
            # Adding to list that contains all tweets
            tweets_list.append({'created_at': tweet.created_at,
                                'tweet_id': tweet.id,
                                'tweet_text': tweet.text})
        return pd.DataFrame.from_dict(tweets_list)

    except BaseException as e:
        print('failed on_status,', str(e))
        time.sleep(3)