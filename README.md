# calcibot
Bearer token, authorising token are needed from the twitter api. 
To do this, one must first create a developer account, and then assign the appropriate values in the code block following the comment,
#login with twitter api
The code that would need new values assigned to it, is
bearer_token=''
auth = tweepy.OAuthHandler('', '')
auth.set_access_token('', '')


Similarly for the reddit bot, we will need a developer account to access the reddit api.
The client_secret, client_id, username and password will be available after the creation of the reddit account.
Assigning of the appropriate values in the code block follows the comment,
# reddit api login
The code to which new values are to be assigned, is
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     username='',
                     password='',
                     user_agent='calcibot v 1.0' //the changes here only refer to the name and version of your bot, change this value on your discretion)
