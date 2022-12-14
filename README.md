# Twitter Common Follow Finder
## What can this program do
Enter a username (e.g. umsi) to search for the user (e.g. School of Information), and the program looks through School of Information's followers' following lists and shows whom the followers also follow. 

For example, School of Information's followers also follow Elon Musk, President Biden, CNN, etc. 

## How to run the program
1. Download/clone this repo
2. Put your `TwitterSecrets.py` file into the same folder. The file should contain
  - API_Key
  - API_Key_Secret
  - Bearer_Token
  - Access_Token
  - Access_Token_Secret
3. Run `common_follow.py`
4. You should see `* Running on http://127.0.0.1:5000` in your terminal
5. Paste `http://127.0.0.1:5000` to a browser
6. You're good to go
7. To end the program, pleasr press CTRL+C on your terminal

## How does the program work behind the scene
1. User enter a user's username (the target user)
2. The program finds the user's id
3. Use the id to get the follower list
4. Create a `Graph` instance as a network
5. Connect the user to his/her followers (add edges in the network)
6. Find the followings of the followers
7. Connect the followers to their followings (add edges in the network)
8. Find and show the top 3 tier users who have the most followers in the network
9. Find and show tweets that mention both the target user and common-followed users
