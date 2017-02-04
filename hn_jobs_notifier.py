#python3

import requests
import json
import time
import peewee
from pathlib import Path
from pushbullet import Pushbullet
import bs4

# currently this script keeps itself running with a main
# loop that executes very 5 min.  A better way may perhaps be to use
# cron or some type of scheduling framework.

# This is what you need to change each month manually until I
# Can make it more dynamic
# To find the latest one go here: https://news.ycombinator.com/submitted?id=whoishiring
LATEST_WHOS_HIRING_THREAD_NUMBER = '13541679'
# I checked and this is the latest number for this month

# Constants you will need to edit with your own info
# Really, these should be imported from the environment
SLACK_WEBHOOK_URL = 'http://your_slack_webhook_url'
# If you want to use pusbullyet, edit this.
# I stopped using pushbullet (for this) because of API rate limits for the free
# version. So, if you use it you will need also to uncomment it out in main() below 
PUSHBULLET_ACCESS_TOKEN = 'your_pb_access_token'

# These should stay the same
BASE_URL = 'https://hacker-news.firebaseio.com'
API_VER = 'v0'
HN_OBJECT = 'item'

# To change what text causes the script to alert the user to a new match
# edit the function called contains_matches()



# Functions for sending messages
def send_pb_msg(title, msg):

    try:
        pb = Pushbullet(PUSHBULLET_ACCESS_TOKEN)
        push = pb.push_note(title, msg)

    except ConnectionError:
        error_message = traceback.format_exc()
        print(error_message)
        # logging.error("!!!!A ConnectionError occurred in send_pb_message:!!!!")
        # logging.error(error_message)
        time.sleep(20)

def send_slack_msg(message):

    message = {'text':message}
    message = json.dumps(message)

    data = {'payload': message}

    r = requests.post(url=SLACK_WEBHOOK_URL, data=data)
    print(r.text)
# End Of Functions for sending messages



# Database setup stuff
db = peewee.SqliteDatabase('hn_notifier.db')

class Comment(peewee.Model):
    comment_id = peewee.CharField()
    text = peewee.CharField()
    has_match = peewee.BooleanField()
    time_posted = peewee.IntegerField(null = True)

    class Meta:
        database = db

def comment_id_in_db(comment_id):
    result = Comment.select().where(Comment.comment_id == comment_id).exists()
    return result


db_file = Path('./hn_notifier.db')
if not db_file.is_file():
    db.create_table(Comment)

db.connect()
# End of Database setup stuff



# helper functions for working with hn API and the data from it
def get_item(item_num):
    r = requests.get('{}/{}/{}/{}.json?print=pretty'.format(BASE_URL,
                                                            API_VER,
                                                            HN_OBJECT,
                                                            item_num))
    return r.text

def contains_matches(to_search):
    """There are better ways to do this, but this will work for now."""
    match1 = 'Python'
    match2 = 'python'
    if (match1 in to_search) or (match2 in to_search):
        return True
    else:
        return False

def extract_html(html):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return text

def decode_hn_json(request_text, hn_object_id):
    try:
        request_json = json.loads(request_text)
        return request_json
    except json.decoder.JSONDecodeError:
        url_template = 'https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty'.format(HN_OBJECT)
        message = 'There was a json.decoder.JSONDecodeError when trying to decode {}\n'.format(HN_OBJECT)
        message = message + 'Visit {} to view what the error could be.'.format(url_template)
        send_pb_msg(message)

# END OF helper functions for working with hn API and the data from it



# Main Loop
# TODO This really needs to be refactored and modularized big time
def main():
    running = True

    while running:
        r = get_item(LATEST_WHOS_HIRING_THREAD_NUMBER)
        r = json.loads(r)
        comments = r['kids']

        for comment in comments:
            # Need to first check if item is in database already
            if not comment_id_in_db(comment):
                print('checking comment #{}'.format(comment))

                # make another request to get the comments info
                r = get_item(comment)
                #print('|{}|'.format(r))
                if r == 'null\n':
                    continue
                    # somehow the hn api allows values of 'null'
                r = decode_hn_json(r, comment)

                try:
                    if contains_matches(r['text']):
                        print(r['id'])
                        print(r['text'])
                        html = extract_html(r['text'])
                        has_match = True
                        message = '*New Hacker News Job Match!*\n' + html
                        #send_pb_msg('NEW HN MATCH!', r['text'])
                        send_slack_msg(message)

                    else:
                        has_match = False

                    com = Comment(comment_id=r['id'], text=r['text'], has_match=has_match, time_posted=r['time'])
                    com.save()

                except KeyError:
                    print('A KeyError occurred.')
                    com = Comment(comment_id=r['id'], text='KeyError', has_match=False)
                    com.save()

        db.close()
        print('Cycle Complete.  Sleeping for 5 min...')
        time.sleep(300)
        # End of main loop

if __name__ == '__main__':
    main()



