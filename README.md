<snippet>
  <content><![CDATA[
# ${1:EECS-510 Tweepy}
This project extracts tweets from user timeline, search queries, and streaming.   
## Resource requirements
  * tweepy
  * json
  * pandas

## Usage

This project contains four commands:

```
python search.py measles > measles_search.txt
```
It uses the Search API to download the 1,000 recent tweets that contain the selected query. The first parameter corresponds to the query (hashtag, word, etc), and the second is the name of the output file. The command saves the results in a TXT file, where each row represents the JSON data of a tweet.  

```
python user.py dgzara > dgzara.txt
```
It downloads the most recent tweets from an user and saves them in a file. The first parameter is the username, and the second is the name of the output file. Twitter API Search restricts to 3,200 tweets per user. The command saves the results in a TXT file, where each row represents the JSON data of a tweet. 

```
python stream.py measles > measles_streaming.txt
```
It extracts streaming live tweets that contain the selected query. The first parameter is the query (hashtag, word, etc), and the second is the name of the output file. It saves the results in a TXT file, where each row represents the JSON data of a tweet. 

```
python analysis.py measles_search.txt
```
It transforms the generated TXT files into a pandas Dataframe. 