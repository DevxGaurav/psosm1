import pickle
import re as regex
import string

import nltk
import pandas as pd
import tweepy

nltk.download('stopwords')
nltk.download('punkt')

consumerKey = "KFPMToaksFgIkBlGk19I61q9R"
consumerSecret = "bcM3pNejcRj4jS866AkUhtamATiokY6ynzcqBdopVPvYyKhr5G"
accessToken = "1250046040998199298-FGNpKiFxw2JDsl3uNyQuVF2JQtz61a"
accessTokenSecret = "aHzdmUkiPVC67A8sTORWZoDIMzt7swoWMa8JCWnqwF4aW"
useless_words = nltk.corpus.stopwords.words("english") + list(string.punctuation)
authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
authenticate.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(authenticate, wait_on_rate_limit=True)

import urllib 

fie=urllib.request.urlopen('https://github.com/theshmesh/psosm1/blob/master/model/classifier_intro_extrovert.sav?raw=true')
print("Downloaded fie")
introvert_extrovert = pickle.load(fie)

fis=urllib.request.urlopen('https://github.com/theshmesh/psosm1/blob/master/model/classifier_intuition_sensing.sav?raw=true')
print("Downloaded fis")
intuition_sensing = pickle.load(fis)

ftf=urllib.request.urlopen('https://github.com/theshmesh/psosm1/blob/master/model/classifier_thinking_feeling.sav?raw=true')
print("Downloaded ftf")
thinking_feeling = pickle.load(ftf)

fjp=urllib.request.urlopen('https://github.com/theshmesh/psosm1/blob/master/model/classifier_judging_percieving.sav?raw=true')
print("Downloaded fjp")
judging_perceiving =pickle.load(fjp) 


def removeCrap(text):
    # Removing @mentionsc
    text = regex.sub('@[A-Za-z0–9]+', '', text)
    # Removing '#' hash tag
    text = regex.sub('#', '', text)
    # Removing RT
    text = regex.sub('RT[\s]+', '', text)
    # Removing hyperlink
    text = regex.sub('https?:\/\/\S+', '', text)
    return text


def fetchPosts(username):
    try:
        postCount = 0
        allPosts = []
        userPosts = []
        posts = api.user_timeline(username, count=200, tweet_mode='extended')
        for post in posts:
            allPosts.append(post._json)
            userPosts.append(post._json['full_text'])

        limit_id = allPosts[-1]['id']-1
        while len(posts) > 0:
            posts = api.user_timeline(username, count=200, max_id=limit_id, tweet_mode='extended')
            for post in posts:
                allPosts.append(post._json)
                userPosts.append(post._json['full_text'])

            limit_id = allPosts[-1]['id']-1
            postCount += 1
            if postCount >= 400:
                break

        return userPosts
    except:
        return None


def build_bag_of_words_features_filtered(words):
    words = nltk.word_tokenize(words)
    return {word: 1 for word in words if word not in useless_words}


def classifyPost(post):
    tokenize = build_bag_of_words_features_filtered(post)
    inex = introvert_extrovert.classify(tokenize)
    inse = intuition_sensing.classify(tokenize)
    thfe = thinking_feeling.classify(tokenize)
    jupe = judging_perceiving.classify(tokenize)
    mbt = ''
    if inex == 'introvert':
        mbt += 'I'
    if inex == 'extrovert':
        mbt += 'E'
    if inse == 'Intuition':
        mbt += 'N'
    if inse == 'Sensing':
        mbt += 'S'
    if thfe == 'Thinking':
        mbt += 'T'
    if thfe == 'Feeling':
        mbt += 'F'
    if jupe == 'Judging':
        mbt += 'J'
    if jupe == 'Percieving':
        mbt += 'P'
    return mbt


def predict(posts):
    a = []
    trait1 = pd.DataFrame([0, 0, 0, 0], ['I', 'N', 'T', 'J'], ['count'])
    trait2 = pd.DataFrame([0, 0, 0, 0], ['E', 'S', 'F', 'P'], ['count'])
    for i in posts:
        a += [classifyPost(i)]
    for i in a:
        for j in ['I', 'N', 'T', 'J']:
            if j in i:
                trait1.loc[j] += 1
        for j in ['E', 'S', 'F', 'P']:
            if j in i:
                trait2.loc[j] += 1
    trait1 = trait1.T
    trait1 = trait1 * 100 / len(posts)
    trait2 = trait2.T
    trait2 = trait2 * 100 / len(posts)

    # Finding the personality
    yourTrait = ''
    percentage = {}
    for i, j in zip(trait1, trait2):
        temp = max(trait1[i][0], trait2[j][0])
        percentage[i] = trait1[i][0]
        percentage[j] = trait2[j][0]
        # print('temp', temp)
        # print('trait1[i][0]', trait1[i][0])
        # print('trait2[i][0]', trait2[j][0])
        if trait1[i][0] == temp:
            yourTrait += i
        elif trait2[j][0] == temp:
            yourTrait += j
    return yourTrait, percentage
