import random
from collections import Counter
 
 
def jaccard(set_1, set_2):
    set_1 = set(set_1)
    set_2 = set(set_2)
    return len(set_1.intersection(set_2)) / float(len(set_1.union(set_2)))
 
 
def find_most_similar_user(user_likes, others_likes, users_count=10):
    # user_like - list of post ids
    # others likes - dictionary, where key is user name and value is list of post ids
    # find users that like what you like and find what they liked that you did not
    # if our user didn't like anything: return random
    if len(others_likes) < users_count:
        users_count = len(others_likes)
    if not others_likes:
        return []
    if not user_likes:
        similar_users = others_likes.keys()
        similar_users = [(user, random.random()) for user in similar_users()]

    else:
        # using jaccard coefficient
        similar_users = []
        for user, ulikes in others_likes.items():
            # calculate similarity and append user name and score to list
            similar_users.append((user, jaccard(user_likes, ulikes)))
        # now sort the list of users to find most similar
        # similar_users.sort(key=lambda x: x[1], reverse=True)
        # return only list of scores, maximum 'users_count' of them
        #similar_users = [(user, score) for user, score in similar_users[:users_count]]
    return similar_users


def recommend(user, news, n = 10):
    # Based on all news, find what current user did not like yet but might
    #
    # Gather users likes and others likes
    likes = {}
    all_news = {}
    for post in news:
        for user_name in post['likes']:
            if user_name not in likes:
                likes[user_name] = set()
            likes[user_name].add(post['_id'])
        all_news[post['_id']] = post
    # if not likes:
    #     return []
    # now get likes of current user
    user_likes = likes.get(user, [])
    # Delete key-value pair from dict, where key is a name of our user
    if user in likes:
        del likes[user]
    # find 10 most similar users
    most_similar_users = find_most_similar_user(user_likes, likes, 100)
   # print("Most similar users:")
   # print(most_similar_users)
    # get their likes into Counter: we will count most liked posts
    possible_items = Counter()
    for user_name, score in most_similar_users:
        for post_id in likes[user_name]:
            if post_id not in user_likes:
                possible_items[post_id] += score
    # return up to 'n' most liked posts that are not liked by our user
    return [all_news[post_id] for post_id, _ in possible_items.most_common(n)]
