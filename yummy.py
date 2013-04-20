import jinja2
import os
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import channel
from google.appengine.api import memcache
from cors.cors_application import CorsApplication
from cors.cors_options import CorsOptions
from yummy_model import *

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

script_file = "<script type='text/javascript' src='/script.js'></script>"

class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {"warning": "Building Channel...", 
                              "script_file": script_file}
        template = jinja_environment.get_template("groups.html")
        self.response.out.write(template.render(template_values))

class LoginPage(webapp2.RequestHandler):
    def get(self):
        return

class ChatPage(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        avatar_url = self.request.get("avatar_url")
        token = channel.create_channel(name)
        template_values = {"warning": "Building Channel...", 
                              "script_file": script_file, 
                              "name" : name, 
                              "avatar_url": avatar_url, 
                              "token": token}
        template = jinja_environment.get_template("chat_page.html")
        self.response.out.write(template.render(template_values))

class ChatRequest(webapp2.RequestHandler):
    def get(self):
        chat_html = get_data("chathtml", "Chat")
        if chat_html != None:
            self.response.out.write(chat_html.html)
            return
        chat = Chat.query(Chat.chat_id == "chat").get()
        if chat == None:
            self.response.out.write("error")
            return
        chat_log = json.loads(chat.chat_log)
        new_chat_log = []
        for chat_line in chat_log:
            new_chat_log.append(json.loads(chat_line)) 
        template_values = {"chat_log": new_chat_log}
        template = jinja_environment.get_template("chat_log.html")
        self.response.out.write(template.render(template_values)) 

    def post(self):
        chat = Chat.query(Chat.chat_id == "chat").get()
        if chat == None:
            self.response.out.write("error")
            return
        chat_content = self.request.get("chat")
        chat_log = json.loads(chat.chat_log)
        chat_log.append(chat_content)
        chat.chat_log = json.dumps(chat_log)
        chat.put()
        chat_html = ChatHTML.query(ChatHTML.chat_id == "chat").get()
        if chat_html == None:
            chat_html = ChatHTML()
        new_chat_log = []
        for chat_line in chat_log:
            new_chat_log.append(json.loads(chat_line)) 
        template_values = {"chat_log": new_chat_log}
        template = jinja_environment.get_template("chat_log.html")
        chat_html.init_html(template.render(template_values))
        memcache.set("chathtml", chat_html, 5)
        chat_tokens = json.loads(chat.chat_tokens)
        for name in chat_tokens:
            channel.send_message(name, "chat_change")

class SketchPage(webapp2.RequestHandler):
    def get(self):
        return

class SketchRequest(webapp2.RequestHandler):
    def get(self):
        return

    def post(self):
        return

class Connected(webapp2.RequestHandler):
    def post(self):
        chat = Chat.query(Chat.chat_id == "chat").get()
        if chat == None:
            chat = Chat()
            chat.init_chat()
        chat.user_num += 1
        tokens = json.loads(chat.chat_tokens)
        token = self.request.get('from')
        tokens.append(token)
        chat.chat_tokens = json.dumps(tokens)
        chat.put()

class Disconnected(webapp2.RequestHandler):
    def post(self):
        chat = Chat.query(Chat.chat_id == "chat").get()
        chat.user_num -= 1
        if chat.user_num == 0:
            chat.init_chat()
        else:
            tokens = json.loads(chat.chat_tokens)
            token = self.request.get('from')
            tokens.remove(token)
            chat.chat_tokens = json.dumps(tokens)
        chat.put()
        
route_id = "<group_id:[A-Za-z0-9_]+>"
base_app = webapp2.WSGIApplication([('/', MainPage), 
    ('/login', LoginPage), webapp2.Route('/group/' + route_id, ChatPage), 
    webapp2.Route('/group/' + route_id + '/playerConnect', ChatRequest), 
    webapp2.Route('/game/' + route_id + '/status', SketchPage), 
    webapp2.Route('/game/' + route_id + '/visibleTable', SketchRequest), 
    ('/_ah/channel/connected/', Connected), 
    ('/_ah/channel/disconnected/', Disconnected)], debug=True)
app = CorsApplication(base_app, 
                      CorsOptions(allow_origins=True, continue_on_error=True))