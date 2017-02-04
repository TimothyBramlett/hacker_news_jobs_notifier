# hacker_news_jobs_notifier
A messy script I threw together a few years ago when looking for a dev job

Throwing this up here for a friend who is looking for a job and may find this helpful

# How this works

So a couple of years ago when I was searching for jobs I wanted to be notified via pusbullet or Slack (on my personal Slack Team) of when new Hacker News Jobs posts showed up that matched the search terms "Python" or "python".

This script connects to a specified thread/object on the Hacker News API, every 5 minutes, and reads all the comments of that thread, that it has never 'seen' before.

If it hasn't "seen" the comment before then it adds it to the database. Then it also looks at the text and uses the `contains_matches()` function to see if it can find the appropriate search string.  If so, notifications occur in Slack via Slack's Webhook functionality.

# How to use

1. Setup your own personal Slack team and create a Webhook into one of your channels
2. If you want to use pusbullet, then setup a pushbullet account and create a pusbullet API key
3. Make sure you have Python 3 installed and setup a Virtual Environment, if needed for this project.
4. Using Python 3 install the libraries listed in `requirements.txt`. Usually, `pip install -r requirements.txt` will work.
5. Run the script with Python 3 and leave it running
6. Monitor your Slack Channel and you can keep track of messages/jobs you like or indicate that you have read them already by starring messages or adding some other kind of reaction.

# Which version of Python?

This was designed to run on Python 3
