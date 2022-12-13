from flask import Flask, render_template, request
from final_project import Graph, build_network, find_common_followers, find_name_by_username, network_degrees, clean_username
app = Flask(__name__)
@app.route('/', methods=['POST','GET'])
def index():     
    username = ''
    result = []
    name = ''
    degrees = {}
    error = False
    num_sampled_followers = 0
    if request.method =='POST' and request.values['submit']=='Submit':
        username = request.values['username']
        username = clean_username(username)
        try:
            name = find_name_by_username(username)
        except:
            error = True
        else:
            #name = find_name_by_username(username)
            test_network2 = Graph()
            network2 = build_network(username, test_network2)
            result = find_common_followers(username, network2)
            degrees = network_degrees(username, network2)
            num_sampled_followers = len(degrees['first'])
    


    return render_template('index.html', username=username, name=name, result=result, degrees=degrees, error=error, num_sampled_followers=num_sampled_followers)
if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(debug=True)