from google.appengine.ext import db

# The datastore model for the app; a simple model which stores text, status and date
# created
class StickyNote(db.Model):

    author = db.StringProperty()
    text = db.StringProperty(multiline=True)
    status = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    
