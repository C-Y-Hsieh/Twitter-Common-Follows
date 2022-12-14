import requests
import os
import json
import TwitterSecrets


bearer_token = TwitterSecrets.Bearer_Token

USER_ID = '1009984504247676928' #temp test
follower_url = f"https://api.twitter.com/2/users/{USER_ID}/followers"
following_url = f"https://api.twitter.com/2/users/{USER_ID}/following"
user_url = "https://api.twitter.com/2/users"
user_by_url = user_url + '/by'
search_url = "https://api.twitter.com/2/tweets/search/recent"

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

CACHE_FILENAME = "cache.json"

def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the CACHE dictionary.

    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def construct_unique_key(baseurl, params):
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

def twitter_with_cache(baseurl, params):
    ''' Get data from cache, If no cache, then get data from the API.

    Parameters
    ----------
    baseurl: string
        the base endpoint of the API
    params: dic
        the parameters to query

    Returns
    -------
    The opened cache
    '''
    unique_key = construct_unique_key(baseurl, params)
    if unique_key in CACHE:
        return CACHE[unique_key]
    else:
        CACHE[unique_key] = connect_to_endpoint(baseurl, params) 
        save_cache(CACHE)
        return CACHE[unique_key]

CACHE = open_cache()

class User:
    def __init__(self, id, name, username):
        self.id = id
        self.name = name
        self.username = username
        self.connectedTo = []

    
    def addNeighbor(self, nbr):
        '''
        nbr (User): another vertex connected to this vertix
        '''
        self.connectedTo.append(nbr)
    def getId(self):
        return self.id
    def getConnections(self):
        return self.connectedTo
    def getConnectionIds(self):
        ids = [x.id for x in self.connectedTo]
        return ids
    def __str__(self):
        return str(self.id) + ' is connected to ' + str([x.id for x in self.connectedTo])

class Graph:
    def __init__(self):
        self.vertList = {} 
        self.numVertices = 0

    def addVertex(self, key, name, username): ## avoid repetitive?
        self.numVertices = self.numVertices + 1
        newVertex = User(key, name, username)
        self.vertList[key] = newVertex
        return newVertex

    def getVertex(self,n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertList

    def addEdge(self,Follower_key, Followed_key, follower_name='name', followed_name='name2', follower_username='username1', followed_username='username2'):
        '''
        follower -> followed
        '''
        if Follower_key not in self.vertList.keys():
            self.addVertex(Follower_key, follower_name, follower_username)
            # print(f"create a new vertix: {V1_key}")
        if Followed_key not in self.vertList.keys():
            self.addVertex(Followed_key, followed_name, followed_username)
            # print(f"create a new vertix: {V2_key}")
        if self.vertList[Followed_key] not in self.vertList[Follower_key].getConnections(): # if the edge doesn't exist
            self.vertList[Follower_key].addNeighbor(self.vertList[Followed_key])

    def getVertices(self):
        return self.vertList.keys()

    def adjList(self):
        adjList = []
        for v_key in self.vertList.keys():
            adjList.append(self.vertList[v_key].getConnectionIds())
        return adjList


    def __iter__(self):
        return iter(self.vertList.values())

def clean_username(input):
    '''
    Remove @ and space of user input.

    Parameters
    ----------
    input: str
        The Twitter username that the user want to search for
    
    Returns
    ----------
    str
        Cleaned data of the username
    '''
    return input.strip().replace('@', '')

def find_name_by_username(target_username):
    '''
    Find the user's display name on Twitter

    Parameters
    ----------
    target_username: str
        The Twitter username that the user want to search for
    
    Returns
    ----------
    name: str
        The display name of the username
    '''
    target_username = clean_username(target_username)
    name = twitter_with_cache(user_by_url, {'usernames': target_username})
    name = name['data'][0]['name']
    return name

def build_network(target_username, network, number=14):
    '''
    Build a network based on the given user, the user's followers, and the followers' followings.

    Parameters
    ----------
    target_username: str
        A Twitter username
    network: Graph
        A empty Graph instance
    number:
        The number of sampled followers

    Returns
    ----------
    network: Graph
        The network contains the target user, the user's followers, and the followers' followings.
    '''
    target_username = clean_username(target_username)
    target = twitter_with_cache(user_by_url, {'usernames': target_username})
    target_id = target['data'][0]['id']
    target_name = target['data'][0]['name']
    follower_url = f"https://api.twitter.com/2/users/{target_id}/followers"

    followers = twitter_with_cache(follower_url, {'max_results': number})
    for user in followers['data']:
        network.addEdge(user['id'], target_id, user['name'], target_name, user['username'], target_username)
        
        follower_id = user['id']
        following_url = f"https://api.twitter.com/2/users/{follower_id}/following"
        following = twitter_with_cache(following_url, {})
        if 'errors' not in following.keys(): # some users might lock their account so I don't have permit to see their following
            for f in following['data']:
                network.addEdge(user['id'], f['id'], user['name'], f['name'], user['username'], f['username'])

    return network






def find_common_followers(target_username, network):
    '''
    Find top3 tier users whom the target user's followers also follow.
    For example, Umich (target user)'s followers also follow Michigan Athletics, Elon Musk, etc.
    
    Parameters
    ----------
    target_username: str
        A Twitter username
    network: Graph
        The network contains the target user, the user's followers, and the followers' followings.

    Returns
    ----------
    most_names_dic: dic
        The dictionary contains the top 3 popular users that followers also follow, and the numbers that how many people in the network follow them
        e.g.
        {'first': {'number': 5,'user': [('Michigan Athletics 〽️', 'UMichAthletics'),('Elon Musk', 'elonmusk')]},
        'second': {'number': 4, 'user': [('Aidan Hutchinson', 'aidanhutch97'),("Michigan Men's Basketball", 'umichbball')]},
        'third': {'number': 3, 'user': [('#2⃣BeSavage', 'blake_corum')]}}
    '''
    print(f"username: {target_username,}")
    print(f"# of users in the network: {len(network.vertList)}")
    top_dic = {}
    most = {
        'first': [('', 0)],
        'second': [('', 0)],
        'third': [('', 0)]
    }
    
    user_id = twitter_with_cache(user_by_url, {'usernames': target_username})
    user_id = user_id['data'][0]['id']
    for key in network.vertList.keys():
        for id in network.vertList[key].getConnectionIds():
            if id not in top_dic.keys():
                top_dic[id] = 1
            else:
                top_dic[id] += 1
    
    for id in top_dic.keys():
        if id != user_id:
            if top_dic[id] > most['first'][0][1]: #exclude the target user
                most['third'] = most['second']
                most['second'] = most['first']
                most['first'] = [(id, top_dic[id])]
            elif top_dic[id] == most['first'][0][1]:
                most['first'].append((id, top_dic[id]))
            elif top_dic[id] > most['second'][0][1]:
                most['third'] = most['second']
                most['second'] = [(id, top_dic[id])]
            elif top_dic[id] == most['second'][0][1]:
                most['second'].append((id, top_dic[id]))
            elif top_dic[id] > most['third'][0][1]:
                most['third'] = [(id, top_dic[id])]
            elif top_dic[id] == most['first'][0][1]:
                most['third'].append((id, top_dic[id]))

    most_names_dic = {}
    for key in most.keys():
        if len(most[key]) > 100:
            most_names_dic[key] = 'more than 100 users'
        else:
            user_string = ",".join([u[0] for u in most[key]])
            most_users = twitter_with_cache(user_url, {'ids': user_string})
            most_username = [(i['name'], i['username']) for i in most_users['data']]
            most_names_dic[key] = {
                'number': most[key][0][1]
            }
            most_names_dic[key]['user'] = most_username
    #print(most_names_dic)
    return most_names_dic

def network_degrees(target_username, network):
    '''
    Categorize users in the network into different degrees. The center is the target user.

    Parameters
    ----------
    target_username: str
        The center (target) user used to build the network
    network: Graph
        The network contains the target user, the user's followers, and the followers' followings.

    Returns
    ----------
    degree_of_separation: dic
        A dictionary records the first and second degrees of users.
        The first degree is the follower of the target user.
        The second degree is the followings of the followers
    '''
    target_username = clean_username(target_username)
    id = twitter_with_cache(user_by_url, {'usernames': target_username})['data'][0]['id']
    degree_of_separation = {
        'first': [],
        'second': [],
    }
    for key in network.vertList.keys():
        if id in network.vertList[key].getConnectionIds():
            degree_of_separation['first'].append(network.vertList[key].name)
        elif key != id:
            degree_of_separation['second'].append(network.vertList[key].name)

    return degree_of_separation

def both_mentioned_tweet(string1, string2):
    '''
    Find tweets that contain both usernames (strings).

    Parameters
    ----------
    string1: str
        A username (string)
    string2: Graph
        Another username (string)

    Returns
    ----------
    tweets: list
        A list contains tweeets that mention both usernames (strings)
    '''
    # Don't want to show too much data so only take the first 3 tweets
    tweets = twitter_with_cache(search_url, {'query': f"{string1} {string2}",'max_results': 10})
    tweets = tweets['data'][:3]
    # for t in tweets:
    #     print('====')
    #     print(t['text'])
    return tweets

# def main():
#     # Test
#     test_network = Graph()
#     username = 'official_ONEWE'
#     network1 = build_network(username, test_network)
#     find_common_followers(username, network1)

# if __name__ == "__main__":
#     main()