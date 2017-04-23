#!/usr/bin/python

import sys, tweepy, json
from tweepy import OAuthHandler
from credentials import *

# Twitter only allows access to a users most recent 3240 tweets with this method
def get_user_tweets(screen_name):
    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        
        alltweets = []    
        
        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = screen_name,count=200)
        
        #save most recent tweets
        alltweets.extend(new_tweets)
        
        #save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        
        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            #all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
            
            #we save the tweets
            for i, row in enumerate(new_tweets):    
                print(json.dumps(row._json))
                
            #save most recent tweets
            alltweets.extend(new_tweets)
            
            #update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1
    except:
        print "Unexpected error:", sys.exc_info()[0]
        sys.exit(2)
        
if __name__ == '__main__':
    try:
    	# Pass in the commander line the username of the account
        query = sys.argv[1]
        get_user_tweets(query)
    except IndexError:
        print 'No username added'
        sys.exit(2)