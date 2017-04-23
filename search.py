#!/usr/bin/python

import sys, tweepy, json
from tweepy import OAuthHandler
from credentials import *

# Twitter only allows access to a users most recent 1000 tweets with this method
def search_tweets(query):
    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        max_tweets = 1000

        searched_tweets = []
        last_id = -1
        while len(searched_tweets) < max_tweets:
            count = max_tweets - len(searched_tweets)
            try:
                new_tweets = api.search(q=query, count=count, max_id=str(last_id - 1))
                if not new_tweets:
                    break
                for i, row in enumerate(new_tweets):    
                    print(json.dumps(row._json))
                searched_tweets.extend(new_tweets)
                last_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                break
    except:
        print "Unexpected error:", sys.exc_info()[0]
        sys.exit(2)


if __name__ == '__main__':
    try:
    	# Pass in the commander line the username of the account
        query = sys.argv[1]
        search_tweets(query)
    except IndexError:
        print 'No query added'
        sys.exit(2)