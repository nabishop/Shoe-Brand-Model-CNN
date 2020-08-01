import tweepy
import re
from tweepy import OAuthHandler
from textblob import TextBlob
from twitter.analyzed_tweet_query import AnalyzedTweets


class TwitterClient:
    TWEET_SENTIMENT = "sentiment"
    TWEET_TEXT = "text"

    def __init__(self):
        # twitter dev
        consumer_key = '4Ktu2wLbENVSsxa9XgImXNIuL'
        consumer_secret = 'tiBUh4J57vzmW4n8CQOIjIS48CnFTv0YrISRlIoDyBtMdtzH2s'
        access_token = '1010030390797451264-f2F9p3xegThmA7FVKG3e9nFdEjemxs'
        access_token_secret = 'QTE2jgLx7xOIQcMmHI7MEHQEusa8cJ7MPdOYu8Y0k9HGt'

        # attempt authentication
        try:
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    # removes links, special characters
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])| (\w+:/\S+)", " ", tweet).split())

    # returns 1 for positive, 0 for neutral, -1 for negative
    def get_tweet_sentiment(self, tweet):
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.sentiment.polarity

    def get_tweets_for_query(self, query, count=500):
        tweets = []

        try:
            fetched_tweets = self.api.search(q=query, count=count)

            for tweet in fetched_tweets:
                parsed_tweet = {self.TWEET_TEXT: tweet.text, self.TWEET_SENTIMENT: self.get_tweet_sentiment(tweet.text)}

                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

                    # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            print("Error : " + str(e))

    def analyze_tweets_for_query(self, tweets):
        pos_tweets = 0
        neut_tweets = 0
        neg_tweets = 0

        for tweet in tweets:
            sentiment = tweet[self.TWEET_SENTIMENT]
            if sentiment > 0:
                pos_tweets += 1
            elif sentiment < 0:
                neg_tweets += 1
            else:
                neut_tweets += 1

        return AnalyzedTweets(pos_tweets, neut_tweets, neg_tweets)

    # returns map of shoe name -> sentiment
    def get_sentiments_for_query(self, query):
        tweets = self.get_tweets_for_query(query)
        if tweets is None or len(tweets) == 0:
            return None

        analysis = self.analyze_tweets_for_query(tweets)
        print(analysis)
        return {query: analysis}
