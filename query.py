from twitter import *
from keys import *
import pprint
import re
import urllib
from firebase import *
from firebase_admin import db

def check_twitter():
    t = Twitter(auth=OAuth(TOKEN,
        TOKEN_SECRET,
        CONSUMER_KEY,
        CONSUMER_SECRET), retry=True)
    pp = pprint.PrettyPrinter(indent=4)

    tweets_in_db = []
    mentioned_members_in_db = []
    tweeter_members_in_db = []
    link_resources_in_db = []
    image_resources_in_db = []

    results = t.search.tweets(q="#ethicalCS", tweet_mode="extended")

    # pp.pprint(results["statuses"][0])

    #logistics
    #get the tweetID to prevent duplicate storage
    statuses = [status for status in results["statuses"]]
    retweeted_statuses = [status["retweeted_status"] for status in results["statuses"] if "retweeted_status" in status.keys()]
    quoted_statuses = [status["quoted_status"] for status in results["statuses"] if "quoted_status" in status.keys()]
    statuses += retweeted_statuses + quoted_statuses
    unique_ids = list(set([status["id"] for status in statuses]))
    unique_statuses = []
    for unique_id in unique_ids:
        for status in statuses:
            if status["id"] == unique_id:
                unique_statuses.append(status)
                break
    # pp.pprint(unique_statuses[0]["entities"]["user_mentions"])
    #community building
    tweeters = [status["user"] for status in unique_statuses]
    status_mentions = [status["entities"]["user_mentions"] for status in unique_statuses]
    mentioned_users = [user for mention in status_mentions for user in mention]

    #resource building
    texts = [status["full_text"] for status in unique_statuses]
    status_urls = [re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text) for text in texts]
    resps = [urllib.urlopen(url) for urls in status_urls for url in urls]
    shared_links = [resp.url for resp in resps if "twitter" not in resp.url]
    shared_images = [resp.url for resp in resps if "photo" in resp.url]
    shared_links = list(set(shared_links))
    shared_images = list(set(shared_images))
    #let's save the unique statuses, tweeters, mentioned_users, shared links, and shared photos
    root = db.reference()
    tweets_in_db = [value["tweet_id"] for key, value in db.reference("tweets").get().items()]
    mentioned_members_in_db = [value["user_id"] for key, value in db.reference("members").get().items() if value["member_type"] == "mentioned"]
    tweeter_members_in_db = [value["user_id"] for key, value in db.reference("members").get().items() if value["member_type"] == "tweeter"]
    link_resources_in_db = [value["link"] for key, value in db.reference("resources").get().items() if value["resource_type"] == "link"]
    image_resources_in_db = [value["image"] for key, value in db.reference("resources").get().items() if value["resource_type"] == "image"]

    tweets_added= 0
    for status in unique_statuses:
        if status["id"] not in tweets_in_db:
            tweets_added += 1
            new_status = root.child('tweets').push({
                'tweet_id': status["id"],
                'tweet': status
            })

    tweeters_added = 0
    for tweeter in tweeters:
        if tweeter["id"] not in tweeter_members_in_db:
            tweeters_added += 1
            new_tweeter = root.child('members').push({
                'user_id': tweeter['id'],
                'user_info': tweeter,
                'member_type': 'tweeter'
            })

    users_mentioned = 0
    for user_mention in mentioned_users:
        if user_mention["id"] not in mentioned_members_in_db:
            users_mentioned += 1
            new_mention = root.child('members').push({
                'user_id': user_mention['id'],
                'user_info': user_mention,
                'member_type': 'mentioned'
            })

    links_added = 0
    for shared_link in shared_links:
        if shared_link not in link_resources_in_db:
            links_added += 1
            new_link = root.child('resources').push({
                'link': shared_link,
                'resource_type': 'link'
            })

    images_added = 0
    for shared_image in shared_images:
        if shared_image not in image_resources_in_db:
            images_added += 1
            new_photo = root.child('resources').push({
                'image': shared_image,
                'resource_type': 'image'
            })

    updated_data = {
        "Tweets added": tweets_added,
        "New #ethicalCS users": tweeters_added,
        "Folks mentioned": users_mentioned,
        "New Links": links_added,
        "New Images": images_added
    }

    return updated_data

if __name__ == '__main__':
    check_twitter()


