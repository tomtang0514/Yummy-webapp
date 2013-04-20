#!/usr/bin/env python

from google.appengine.ext import ndb
from google.appengine.api import channel
from google.appengine.api import memcache
import json
import re
import conf

_USER_FIELDS = u'name, email, picture'
class User(ndb.Model):
    """
    name = ndb.StringProperty()
    facebook_id = ndb.StringProperty()
    avatar_url = ndb.StringProperty()
    groups = ndb.TextProperty()
    yummy_list = ndb.TextProperty()
    yummy_history = ndb.TextProperty()
    """
    user_id = ndb.StringProperty(required=True)
    access_token = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    picture = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    # not include anything that's related to friends

    def refresh_data(self):
        me = Facebook().api(u'/me', 
            {u'fields':_USER_FIELDS, u'access_token':self.access_token})
        self.dirty = False # the dirty bit and trigger a refresh of the data
        self.name = me[u'name']
        self.picture = me[u'picture']
        self.email = me.get(u'email')
        return self.put() 

    def init_user(self, name, facebook_id, avatar_url):
        self.name = name
        self.facebook_id = facebook_id
        self.avatar_url = avatar_url
        self.groups = "[]"
        self.yummy_list = "[]"
        self.yummy_history = "[]"

    def join_group(self, group_key):
        groups = json.loads(self.groups)
        if group_key not in groups:
            groups.append(group_key)
            self.groups = json.dumps(groups)

    def quit_group(self, group_key):
        groups = json.loads(self.groups)
        if group_key in groups:
            groups.remove(group_key)
            self.groups = json.dumps(groups)

    def add_restaurant(self, restaurant_key):
        yummy_list = json.loads(self.yummy_list)
        if restaurant_key not in yummy_list:
            yummy_list.append(restaurant_key)
            self.yummy_list = json.dumps(yummy_list)

    def remove_restaurant(self, restaurant_key):
        yummy_list = json.loads(self.yummy_list)
        if restaurant_key in yummy_list:
            yummy_list.remove(restaurant_key)
            self.yummy_list = json.dumps(yummy_list)

    def add_history(self, restaurant_key, time):
        yummy_history = json.loads(self.yummy_history)
        last_idx = len(yummy_history) - 1
        latest_history = yummy_history[last_idx]
        if latest_history[0] == time:
            (yummy_history[last_idx]).append(restaurant_key)
        else:
            history = [time, restaurant_key]
            yummy_history.append(history)
        self.yummy_history = json.dumps(yummy_history)

class Group(ndb.Model):
    name = ndb.StringProperty()
    member_num = ndb.IntegerProperty()
    members = ndb.TextProperty()
    chat_key = ndb.StringProperty()
    sketch_key = ndb.StringProperty()

    def init_group(self, name):
        self.name = name
        self.member_num = 0
        self.members = "[]"
        chat = Chat()
        self.chat_key = chat.init_chat()
        sketch = Sketch()
        self.sketch_key = sketch.init_sketch()

    def join_group(self, user_key):
        members = json.loads(self.members)
        if user_key not in members:
            self.member_num += 1
            members.append(user_key)
            self.members = json.dumps(members)

    def quit_group(self, user_key):
        members = json.loads(self.members)
        if user_key in members:
            self.member_num -= 1
            members.remove(user_key)
            self.members = json.dumps(members)

class Chat(ndb.Model):
    online_num = ndb.IntegerProperty()
    chat_log = ndb.TextProperty()
    chat_tokens = ndb.TextProperty()

    def init_chat(self):
        self.online_num = 0
        self.chat_log = "[]"
        self.chat_tokens = "[]"
        return self.put().urlsafe()

class Sketch(ndb.Model):
    online_num = ndb.IntegerProperty()
    sketch_log = ndb.TextProperty()
    sketch_tokens = ndb.TextProperty()

    def init_sketch(self):
        self.online_num = 0
        self.sketch_log = "[]"
        self.sketch_tokens = "[]"
        return self.put().urlsafe()

class YummyVote(ndb.Model):
    name = ndb.StringProperty()
    restaurant_key = ndb.StringProperty()
    vote = ndb.IntegerProperty()

    def init_vote(self, name, restaurant_key):
        self.name = name
        self.restaurant_key = restaurant_key
        self.vote = 1

'''
class YummyList(ndb.Model):
    name = ndb.StringProperty()
    list_log = ndb.TextProperty()

    def init_list(self, name):
        self.name = name
        self.list_log = "[]"
        return self.put().urlsafe()
'''

class Restaurant(ndb.Model):
    name = ndb.StringProperty()
    location = ndb.StringProperty()
    rating = ndb.FloatProperty()
    rate_num = ndb.IntegerProperty()
    yummy_dishes = ndb.StringProperty()

    def init_restaurant(self, name, location, yummy_dishes):
        self.name = name
        self.location = location
        self.checked = False
        self.rating = 0
        self.rate_num = 0
        self.yummy_dishes = yummy_dishes

    def update_restaurant(self, rating, rate_num, yummy_dishes):
        self.rating = rating
        self.rate_num = rate_num
        self.yummy_dishes = yummy_dishes

'''
class ChatHTML(ndb.Model):
    chat_id = ndb.StringProperty()
    html = ndb.TextProperty()

    def init_html(self, html):
        self.chat_id = "chathtml"
        self.html = html
'''

def get_data(key, type_name):
    data = memcache.get(key)
    if data is not None:
        return data
    return (ndb.Key(urlsafe = key)).get()
    '''
    elif type_name == "Chat":
        data = Chat.query(Chat.chat_id == key).get()
        memcache.add(key, data, 5)
        return data
    else:
        data = ChatHTML.query(ChatHTML.chat_id == key).get()
        memcache.add(key, data, 5)
        return data
    '''

class FacebookApiError(Exception):
    def __init__(self, result):
        self.result = result

    def __str__(self):
        return self.__class__.__name__ + ': ' + json.dumps(self.result)

class Facebook(object):
    """Wraps the Facebook specific logic"""
    def __init__(self, app_id=conf.FACEBOOK_APP_ID,
            app_secret=conf.FACEBOOK_APP_SECRET):
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_id = None
        self.access_token = None
        self.signed_request = {}

    def api(self, path, params=None, method=u'GET', domain=u'graph'):
        """Make API calls"""
        if not params:
            params = {}
        params[u'method'] = method
        if u'access_token' not in params and self.access_token:
            params[u'access_token'] = self.access_token
        result = json.loads(urlfetch.fetch(
            url=u'https://' + domain + u'.facebook.com' + path,
            payload=urllib.urlencode(params),
            method=urlfetch.POST,
            headers={
                u'Content-Type': u'application/x-www-form-urlencoded'})
            .content)
        if isinstance(result, dict) and u'error' in result:
            raise FacebookApiError(result)
        return result

    def load_signed_request(self, signed_request):
        """Load the user state from a signed_request value"""
        try:
            sig, payload = signed_request.split(u'.', 1)
            sig = self.base64_url_decode(sig)
            data = json.loads(self.base64_url_decode(payload))

            expected_sig = hmac.new(
                self.app_secret, msg=payload, digestmod=hashlib.sha256).digest()

            # allow the signed_request to function for upto 1 day
            if sig == expected_sig and \
                    data[u'issued_at'] > (time.time() - 86400):
                self.signed_request = data
                self.user_id = data.get(u'user_id')
                self.access_token = data.get(u'oauth_token')
        except ValueError, ex:
            pass # ignore if can't split on dot

    @property
    def user_cookie(self):
        """Generate a signed_request value based on current state"""
        if not self.user_id:
            return
        payload = self.base64_url_encode(json.dumps({
            u'user_id': self.user_id,
            u'issued_at': str(int(time.time())),
        }))
        sig = self.base64_url_encode(hmac.new(
            self.app_secret, msg=payload, digestmod=hashlib.sha256).digest())
        return sig + '.' + payload

    @staticmethod
    def base64_url_decode(data):
        data = data.encode(u'ascii')
        data += '=' * (4 - (len(data) % 4))
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def base64_url_encode(data):
        return base64.urlsafe_b64encode(data).rstrip('=')



