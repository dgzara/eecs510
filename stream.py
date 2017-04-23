#!/usr/bin/python

import sys
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from credentials import *

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
    	print data.rstrip()
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    try:
    	auth = OAuthHandler(consumer_key, consumer_secret)
    	auth.set_access_token(access_key, access_secret)

    	# We get the query
        query = sys.argv[1]
        
        # We add the query in the stream filter
        stream = Stream(auth, StdOutListener())
        stream.filter(track=[query])
    except IndexError:
        print 'No query added'
        sys.exit(2)