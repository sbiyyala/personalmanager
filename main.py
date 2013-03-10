###### Shishir Biyyala ####
###### Shishir.Biyyala@gmail.com ###

import webapp2
from views import CreateNote, DeleteNote, EditNote, NotePage

# The driver of the app
app = webapp2.WSGIApplication([
        ('/', NotePage),
        ('/notes', NotePage), 
        ('/create', CreateNote), 
        ('/edit/([\d]+)', EditNote),
        ('/delete/([\d]+)', DeleteNote)
        ],
        debug=True)
