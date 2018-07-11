import json
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

class TwitterClient(object):
	'''
	Generic Twitter Class for sentiment analysis.
	'''
	def __init__(self):
		'''
		Class constructor or initialization method.
		'''
		filename = open('.\\settings\\configuration.json', 'r')
		data = json.loads(filename.read())


		twitter_info = data['twitter_secrets']
		consumer_key = twitter_info['consumer_key']
		consumer_secret = twitter_info['consumer_secret']
		access_token = twitter_info['access_token']
		access_token_secret = twitter_info['access_token_secret']

		# attempt authentication
		try:
			# create OAuthHandler object
			self.auth = OAuthHandler(consumer_key, consumer_secret)
			# set access token and secret
			self.auth.set_access_token(access_token, access_token_secret)
			# create tweepy API object to fetch tweets
			self.api = tweepy.API(self.auth)
		except:
			print("Error: Authentication Failed")

	def clean_tweet(self, tweet):
		'''
		Utility function to clean tweet text by removing links, special characters
		using simple regex statements.
		'''
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

	def get_tweet_sentiment(self, tweet):
		'''
		Utility function to classify sentiment of passed tweet
		using textblob's sentiment method
		'''
		# create TextBlob object of passed tweet text
		analysis = TextBlob(self.clean_tweet(tweet))
		# set sentiment
		if analysis.sentiment.polarity > 0:
			return 'positive'
		elif analysis.sentiment.polarity == 0:
			return 'neutral'
		else:
			return 'negative'

	def get_tweets(self, query, count = 10):
		'''
		Main function to fetch tweets and parse them.
		'''
		# empty list to store parsed tweets
		tweets = []

		try:
			# call twitter api to fetch tweets
			fetched_tweets = self.api.search(q = query, count = count)
			print("fetching sentiments for : ", query)
			# parsing tweets one by one
			for tweet in fetched_tweets:
				# empty dictionary to store required params of a tweet
				parsed_tweet = {}

				# saving text of tweet
				parsed_tweet['text'] = tweet.text
				# saving sentiment of tweet
				parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

				# appending parsed tweet to tweets list
				if tweet.retweet_count > 0:
					# if tweet has retweets, ensure that it is appended only once
					if parsed_tweet not in tweets:
						tweets.append(parsed_tweet)
				else:
					tweets.append(parsed_tweet)

			# return parsed tweets
			return tweets

		except tweepy.TweepError as e:
			# print error (if any)
			print("Error : " + str(e))

def sentiments(query):
	# creating object of TwitterClient Class
	api = TwitterClient()
	# calling function to get tweets
	tweets = api.get_tweets(query, count = 200)

	# picking positive tweets from tweets
	ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
	# percentage of positive tweets
	print("Positive tweets percentage: {} %".format(round(100*len(ptweets)/len(tweets),0)))
	# picking negative tweets from tweets
	ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
	# percentage of negative tweets
	print("Negative tweets percentage: {} %".format(round(100*len(ntweets)/len(tweets),0)))
	# percentage of neutral tweets
	neutral_tweets = len(tweets)-len(ptweets)-len(ntweets)
	print("Neutral tweets percentage: {} %".format(round(100*neutral_tweets/len(tweets),0)))
	neg_tweets = round(100*len(ntweets)/len(tweets),0)
	pos_tweets = round(100*len(ptweets)/len(tweets),0)
	neu_tweets = round(100*neutral_tweets/len(tweets),0)
	return (pos_tweets, neg_tweets, neu_tweets)
