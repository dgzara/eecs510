#!/usr/bin/python

"""
This for unit-testing.
"""
import unittest
import shutil
import tempfile
import os

from stream_and_trace import *


class TestDataUtilMethods(unittest.TestCase):

    def test_trace(self):
        temp_path = tempfile.mkdtemp()
        try:
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_key, access_secret)
            tweet_id = "856706927929298944"
            retweet_id = "856622577866952705"
            api = tweepy.API(auth)
            tweet = api.get_status(tweet_id)
            save_dir= os.path.join(temp_path,'sanity_check.tsv')
            actual_output = trace(tweet, api, save_dir)
            # expected_output = [retweet_id]
            # self.assertListEqual(actual_output, expected_output)

            with open(save_dir, 'r') as f:
                actual_file_content = f.read()

            expected_file_content = '856706927929298944\t775507499805839360\t856622577866952705\t14499829\tretweet\n856622577866952705\t14499829\t14499829\t856516875773239296\treply\n856516875773239296\t14499829\t14499829\t856487452432879616\treply\n856487452432879616\t14499829\t14499829\t856435932207210496\treply\n856435932207210496\t14499829\t14499829\t856422839985065985\treply\n856422839985065985\t14499829\t14499829\t856410448031350784\treply\n856410448031350784\t14499829\t14499829\t856267800293330944\treply\n'
            self.assertEqual(actual_file_content, expected_file_content)


        finally:
            shutil.rmtree(temp_path)




if __name__ == '__main__':
    unittest.main()
