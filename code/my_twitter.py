import requests
import json
import codecs
import datetime
from tqdm import tqdm
import time



########################################################
# Imprimer les abonnements d'un compte dans un fichier #
########################################################

def print_friends(node, bearer_token, filename, app=0, retry_time=None, enriched=False):
    retry_time = retry_time or {a: datetime.datetime.now() for a in range(len(bearer_token))}
    
    (rate_exceeded, cursor, ids) = get_friends_one_app(node, bearer_token[app], enriched=enriched)
    while rate_exceeded:
        retry_time[app] = datetime.datetime.now()+datetime.timedelta(seconds=900)
#        print("Rate exceeded for app " + str(app) + " at time ",datetime.datetime.now().time())
        app = (app+1) % len(bearer_token)

        while datetime.datetime.now() < retry_time[app]:
            time.sleep(1)

        (rate_exceeded, cursor, new_ids) = get_friends_one_app(node, bearer_token[app], cursor, enriched)
        ids += new_ids

    with codecs.open(filename,"w") as friends_file:
        json.dump(ids, friends_file)
    
    return(app, retry_time)


def get_friends_one_app(node, bearer_token_app, cursor="-1", enriched=False):
    RATE_EXCEEDED = False
    ids = []
    
    resource_url = ("https://api.twitter.com/1.1/friends/list.json" if enriched
                    else "https://api.twitter.com/1.1/friends/ids.json")
    
    count = "200" if enriched else "5000"
    
    while True:
        r = requests.get(resource_url,
                         params={
                             "user_id" : node,
                             "count" : count,
                             "cursor" : cursor
                         },
                         headers={"Authorization" : "Bearer " + bearer_token_app})

        if r.status_code != 200:
            if r.status_code == 429:
                RATE_EXCEEDED = True
                break
            elif r.status_code in [401, 404]:
                RATE_EXCEEDED == False
                break
            else:
                print("Error " + str(r.status_code) + " on node " + str(node))
                print(r.text)
                RATE_EXCEEDED == False
                break

        response = json.loads(r.text)

        cursor = response["next_cursor"]
        ids += (response["users"] if enriched
               else response["ids"])
                
        if cursor == 0:
            break
                
    return(RATE_EXCEEDED, cursor, ids)



########################################################
# Imprimer tous les tweets d'un compte dans un fichier #
########################################################

def print_tweets(author, bearer_token, filename, since_id, app=0, retry_time=None):
    retry_time = retry_time or {a: datetime.datetime.now() for a in range(len(bearer_token))}

    (rate_exceeded, current_max, timeline) = get_tweets_one_app(author, bearer_token[app], since_id)
    while rate_exceeded:
        retry_time[app] = datetime.datetime.now()+datetime.timedelta(seconds=900)
#        print("Rate exceeded for app " + str(app) + " at time ",datetime.datetime.now().time())
        app = (app+1) % len(bearer_token)

        while datetime.datetime.now() < retry_time[app]:
            time.sleep(1)

        (rate_exceeded, current_max, new_timeline) = get_tweets_one_app(author,bearer_token[app], since_id, current_max)
        timeline += new_timeline
        
    with codecs.open(filename,"w") as tweet_file:
        json.dump(timeline, tweet_file)
        
    return(app, retry_time)


def get_tweets_one_app(author, bearer_token_app, since_id, max_id=None):
    RATE_EXCEEDED = False
    timeline = []
    
    while True:
        params = {
                "user_id" : author,
                "count" : "200",
                "since_id" : since_id,
                "trim_user" : "true",
        }
        
        if max_id: params["max_id"]=max_id
        
        r = requests.get("https://api.twitter.com/1.1/statuses/user_timeline.json",
                         params=params,
                         headers={"Authorization" : "Bearer " + bearer_token_app})
        
        if r.status_code != 200:
            if r.status_code == 429:
                RATE_EXCEEDED = True
                break
            elif r.status_code in [401, 404]:
                RATE_EXCEEDED == False
                break
            else:
                print("Error " + str(r.status_code) + " on node " + str(author))
                print(r.text)
                RATE_EXCEEDED == False
                break

        response = json.loads(r.text)
        timeline += response
        
        if len(response)==0:
            break

        max_id = min([tweet["id"] for tweet in response])-1
                
    return(RATE_EXCEEDED, max_id, timeline)



###################################################################
# Imprimer tous les retweets opérés par un compte dans un fichier #
###################################################################

def print_retweets(author, bearer_token, filename, since_id, app=0, retry_time=None):
    retry_time = retry_time or {a: datetime.datetime.now() for a in range(len(bearer_token))}
    
    (rate_exceeded, current_max, retweets) = get_retweets_one_app(author, bearer_token[app], since_id)
    while rate_exceeded:
        retry_time[app] = datetime.datetime.now()+datetime.timedelta(seconds=900)
#        print("Rate exceeded for app " + str(app) + " at time ",datetime.datetime.now().time())
        app = (app+1) % len(bearer_token)

        while datetime.datetime.now() < retry_time[app]:
            time.sleep(1)

        (rate_exceeded, current_max, new_retweets) = get_retweets_one_app(author,bearer_token[app], since_id, current_max)
        retweets += new_retweets
        
    with codecs.open(filename,"w") as tweet_file:
        json.dump(retweets, tweet_file)
        
    return(app, retry_time)

def get_retweets_one_app(author, bearer_token_app, since_id, max_id=None):
    RATE_EXCEEDED = False
    retweets = []
    
    while True:
        params = {
                "user_id" : author,
                "count" : "200",
                "since_id" : since_id,
                "trim_user" : "true",
        }
        
        if max_id: params["max_id"]=max_id
        
        r = requests.get("https://api.twitter.com/1.1/statuses/user_timeline.json",
                         params=params,
                         headers={"Authorization" : "Bearer " + bearer_token_app})

        if r.status_code != 200:
            if r.status_code == 429:
                RATE_EXCEEDED = True
                break
            elif r.status_code in [401, 404]:
                RATE_EXCEEDED == False
                break
            else:
                print("Error " + str(r.status_code) + " on node " + str(author))
                print(r.text)
                RATE_EXCEEDED == False
                break

        response = json.loads(r.text)

        retweets += [
            (tweet["user"]["id_str"],
             tweet["retweeted_status"]["user"]["id_str"]) for tweet in response if "retweeted_status" in tweet
        ]
        
        if len(response)==0:
            break

        max_id = min([tweet["id"] for tweet in response])-1
                
    return(RATE_EXCEEDED, max_id, retweets)