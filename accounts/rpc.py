import logging
# Log a message each time this module get loaded.
logging.info('Loading %s', __name__)
from utils import webapp, simplejson
from google.appengine.ext import db
from .utils.utils import tpl_path, ROOT_PATH, raise_error
from methods import registered
from utils.gql_encoder import GqlEncoder, encode
from utils.appengine_utilities.sessions import Session
from .model.user import ProfilePicture

class RPCHandler(webapp.RequestHandler):
  # AJAX Handler
  def __init__(self):
    webapp.RequestHandler.__init__(self)
    self.methods = RPCMethods()

 
  def get(self):
    func = None
   
    action = self.request.get('action')
    if action:
      if action[0] == '_':
        self.error(403) # access denied
        return
      else:
        func = getattr(self.methods, action, None)
   
    if not func:
      self.error(404) # file not found
      return
     
    args = ()
    while True:
      key = 'arg%d' % len(args)
      val = self.request.get(key)
      if val:
        args += (simplejson.loads(val),)
      else:
        break
    result = func(*args)
    self.response.out.write(simplejson.dumps(result))
    


class RPCMethods(webapp.RequestHandler):
  """ Defines AJAX methods.
  NOTE: Do not allow remote callers access to private/protected "_*" methods.
  """




  def SubmitProfileEdits(self, *args):
  	session = Session()
  	user = session['user']
  	user.fullname = args[0]
  	if len(args[1]) > 5:  user.email = args[1]
  	user.location = args[2]
  	if len(args[3]) > 8: 
		webpage = args[3]
		if 'http://' not in webpage: webpage = 'http://' + webpage
		try: user.webpage = webpage
		except: 
		      return "Webpage error"
  	user.work_status = args[4]
  	user.aboutme = args[5]
  	if len(args[6]) > 3:
  		user.photo = ProfilePicture.get(args[6])
  	user.put()

		
	# add up all scores for a given quiztaker, and then rank them.
	return str(user.key())


  	
  	
