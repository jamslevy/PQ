import logging
from utils import webapp, simplejson
from google.appengine.ext import db
import string
from google.appengine.api import urlfetch
import string
import urllib
from utils.BeautifulSoup import BeautifulSoup
from .utils import jsonparser as parser
from utils.utils import ROOT_PATH
from utils.gql_encoder import GqlEncoder, encode
from .model.quiz import QuizItem, RawQuizItem,  ContentPage
from .model.proficiency import ProficiencyTopic, Proficiency
import views


   

class RPCMethods(webapp.RequestHandler):
  """ Defines AJAX methods.
  NOTE: Do not allow reload(sys); sys.setdefaultencoding('utf-8')
remote callers access to private/protected "_*" methods.
  """


######## MODEL METHODS ##########  






      	
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
    
    
    
    
