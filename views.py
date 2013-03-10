###### Shishir Biyyala ####
###### Shishir.Biyyala@gmail.com ###

import jinja2
import os
import webapp2
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import users
import re
from HTMLParser import HTMLParser

from models import StickyNote


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

# To linkify any links submitted as plain text. An attempt to make the app useful as a bookmark logger also
url_regex = re.compile(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>\[\]]+|\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\))+(?:\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\)|[^\s`!(){};:'".,<>?\[\]]))""")

matches = []

# A utility class to strip text of html tags (just href's in our case)
class TagStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

# A friendly template creator 
def createTemplate(reqHandler):

    user = None
    if users.get_current_user():
        url = users.create_logout_url(reqHandler.request.uri)
        user = users.get_current_user().nickname()
    else:
        url = users.create_login_url(reqHandler.request.uri)
        
        
    template_values = {
        'user': user,
        'url': url
        }
	
    return template_values

# Link any possible urls to enable them to function as pseudo-bookmarks
def linkify(string):
    return '<a href=\"%s\" target="_blank">%s</a>'%(string,string)

# Delink the url when edit the text; that way there is a consistent way of
# linking it back again. Not the most efficient, but definitely works. 
def delinkify(html):
    s = TagStripper()
    s.feed(html)
    return s.get_data()

def process_match(m):
    matches.append(m.group(0))
    # instead of url, send out the replaced text
    #print m.group(0)

    return linkify(m.group(0))

# A base handler class
class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(
        self,
        filename,
        template_values,
        **template_args
        ):
        template = jinja_environment.get_template(filename)
        self.response.out.write(template.render(template_values))

        
# The default page which has a user's current notes
class NotePage(BaseHandler):
    def get(self):
        notes = StickyNote.all()
        template_values = createTemplate(self)
        notes = notes.filter('author = ', template_values['user'])
        template_values['notes'] = notes
        self.render_template('notes.html', template_values)

# A new note         
class CreateNote(BaseHandler):

    # Upon submission
    def post(self):

        t = self.request.get('text')
        t = url_regex.sub(process_match, t)
        n = StickyNote(author=users.get_current_user().nickname(),
                       text=t,
                       status=self.request.get('status'))
        n.put()
        return webapp2.redirect('/notes')

    # Get method
    def get(self):
        flag = True
        # Get only yours buddy
        notes = StickyNote.all()
        template_values = createTemplate(self)
        notes = notes.filter('author = ', template_values['user'])
        template_values['notes'] = notes
        template_values['flag'] = flag
        
        self.render_template('create.html', template_values)


# Edit/Update existing note        
class EditNote(BaseHandler):

    def post(self, note_id):
        iden = int(note_id)
        note = db.get(db.Key.from_path('StickyNote', iden))

        note.author = users.get_current_user().nickname()
        t = self.request.get('text')
        
        note.text = url_regex.sub(process_match, t)
        note.status = self.request.get('status')
        note.date = datetime.now()
        note.put()
        return webapp2.redirect('/notes')

    def get(self, note_id):
        iden = int(note_id)
        note = db.get(db.Key.from_path('StickyNote', iden))
        # strip the note off of html tags and send it to edit
        note.text = delinkify(note.text)
        notes = StickyNote.all()
        notes = notes.filter('author = ', users.get_current_user().nickname())

        template_values = createTemplate(self)
        template_values['note'] =  note
        template_values['notes'] = notes
        self.render_template('edit.html', template_values)


# Delete existing note 
class DeleteNote(BaseHandler):

    def get(self, note_id):
        iden = int(note_id)
        note = db.get(db.Key.from_path('StickyNote', iden))
        db.delete(note)
        return webapp2.redirect('/notes')
