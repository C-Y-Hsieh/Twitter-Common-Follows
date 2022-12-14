from flask import Flask, render_template, request
from final_project import Graph, build_network, find_common_followers, find_name_by_username, network_degrees, clean_username, both_mentioned_tweet, tweet_url
app = Flask(__name__)
@app.route('/', methods=['POST','GET'])
def index():     
    username = ''
    result = []
    name = ''
    degrees = {}
    error = False
    num_sampled_followers = 0
    both_tweet = []
    cached_list = ["umsi", "umich", "umichfootball", "rbw_mamamoo", "itzyofficial"]

    def combine_both_tweet(result):
        '''
        Loop through all top common follow users and find tweets that mention both of them.

        Parameters
        ----------
        result: dic
            The dictionary contains the top 3 popular users that followers also follow, and the numbers that how many people in the network follow them

        Returns
        ----------
        both_tweet: list
            A list contains tweeets that mention both usernames (strings)
        '''
        both_tweet = []
        for key in result.keys():
                for i in result[key]['user']:
                    try:
                        both_tweet += both_mentioned_tweet(i[1], username)
                    except:
                        pass
        return both_tweet


    if request.method =='POST' and request.values['submit']=='Submit':
        username = request.values['username']
        username = clean_username(username)
        try:
            name = find_name_by_username(username)
        except:
            error = 'no_user'
        else:
            network = Graph()
            if username.lower() in cached_list:
                network = build_network(username, network, 30)
                result = find_common_followers(username, network)
                degrees = network_degrees(username, network)
                num_sampled_followers = len(degrees['first'])
                both_tweet = combine_both_tweet(result)
            else:
                try:
                    network = build_network(username, network)
                except:
                    error = '429'
                else:
                    result = find_common_followers(username, network)
                    degrees = network_degrees(username, network)
                    num_sampled_followers = len(degrees['first'])
                    both_tweet = combine_both_tweet(result)


    return render_template('index.html', username=username, name=name, result=result, degrees=degrees, error=error, num_sampled_followers=num_sampled_followers, both_tweet=both_tweet, tweet_url=tweet_url, cached_list=cached_list)
if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(debug=True)