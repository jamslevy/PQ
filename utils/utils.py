
import os
import logging
from google.appengine.ext import db
from google.appengine.api import users
import webapp.template
from webapp import *
from model.dev import Admin 


ROOT_PATH = os.path.dirname(__file__) + "/.."

global LOGINSTATUS
LOGINSTATUS = "unknown"




def tpl_path(template_file_name):
    return os.path.join(ROOT_PATH,
                        './templates', template_file_name)

                    

def login_text():
  # Construct Login/Logout Text.
  if users.get_current_user():
    LOGINSTATUS = "logged in"
    url_linktext = 'Logout'
  else:
    url_linktext = 'Login'
  return url_linktext




def check_login(LOGINSTATUS):
  # Construct Login/Logout Text.
  if users.get_current_user():
    LOGINSTATUS = "logged in"
  else:
    LOGINSTATUS = "logged out"
  return LOGINSTATUS

def raise_error(error_string):
    # Raise and Log Error
    logging.error(error_string)




def require_login(uri):
  if users.get_current_user():
    LOGINSTATUS = "logged in"
    return LOGINSTATUS
  else:
    redirect(users.create_login_url(uri))




def redirect_to_login(*args, **kwargs):
    return args[0].redirect(users.create_login_url(args[0].request.uri))

def admin_only(handler):
    def wrapped_handler(*args, **kwargs):    
        user = users.get_current_user()
        logging.debug(user)
        if user:
            if users.is_current_user_admin():
                return handler(args[0])
            else:
                logging.warning('An unauthorized user has attempted '
                                'to enter an authorized page')
                return args[0].redirect(users.create_logout_url('/')) 
        else:
            return redirect_to_login(*args, **kwargs)

    return wrapped_handler
        
        
        
def authorized(user):
	"""Return True if user is authorized."""
	auth_user = users.is_current_user_admin()
	if auth_user: return True
	else: return False 
	"""
    else
	    new_user = Admin(key_name = str(user), user = user)
	    new_user.put()
	    return True
	"""
	    
			        



def redirect_from_appspot(wsgi_app): #Turned off for now
    def redirect_if_needed(env, start_response):
        if env.get('HTTP_HOST','').startswith('plopquiz.appspot.com'):
            import webob, urlparse
            request = webob.Request(env)
            scheme, netloc, path, query, fragment = urlparse.urlsplit(request.url)
            url = urlparse.urlunsplit([scheme, 'www.plopquiz.com', path, query, fragment])
            start_response('301 Moved Permanently', [('Location', url)])
            return
        else:
            return wsgi_app(env, start_response)
    return redirect_if_needed
    

def browser_check(wsgi_app):
    def redirect_if_needed(env, start_response):
        if "Mozilla/4.0" in env.get('HTTP_USER_AGENT',()): # MSIE - are there any others we need?
            import webob, urlparse
            request = webob.Request(env)
            if '/js/' in request.url: pass # doesn't apply to script handlers
            scheme, netloc, path, query, fragment = urlparse.urlsplit(request.url)
            error_path = '/error/browser'
            if path == error_path: return wsgi_app(env, start_response) # avoid infinite loops
            url = urlparse.urlunsplit([scheme, netloc,  error_path, query, fragment])
            start_response('301 Moved Permanently', [('Location', url)])
            return
        return wsgi_app(env, start_response)
    return redirect_if_needed

          
# 404
class NotFoundPageHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        path = tpl_path('utils/404.html')
        template_values = {'no_load': True}
        self.response.out.write(template.render(path, template_values))



def GetPathElements():
    '''split PATH_INFO out to a list, filtering blank/empty values'''
    return [ x for x in os.environ['PATH_INFO'].split('/') if x ]

def GetUserAgent():
    '''return the user agent string'''
    return os.environ['HTTP_USER_AGENT']

def Debug():
    '''return True if script is running in the development envionment'''
    return  'Development' in os.environ['SERVER_SOFTWARE']


def hash_pipe(private_object):
    import md5 # TODO use something else
    from google.appengine.api import memcache
    new_hash = md5.md5()
    new_hash.update(str(private_object))
    public_token = new_hash.hexdigest()
    memcache.add(public_token, private_object, 6000) # length?
    return public_token



#### MEMCACHE

def memoize(key, time=1000000):
    """Decorator to memoize functions using memcache."""
    
    def decorator(fxn):
        def wrapper(*args, **kwargs):
            from google.appengine.api import memcache
            data = memcache.get(key)
            if Debug(): return fxn(*args, **kwargs) # not active in dev mode - could this be cause of production expires problem?
            if data is not None:
                return data
            data = fxn(*args, **kwargs)
            memcache.set(key, data, time)
            return data
        return wrapper
    return decorator  

    

### SESSIONS


def set_flash(msg):
	from appengine_utilities.sessions import Session
	session = Session()
	session['flash_msg'] = msg
	return msg


def get_flash(keep=False):
    from appengine_utilities.sessions import Session
    session = Session()
    msg = session['flash_msg']
    if not keep: session['flash_msg'] = False
    return msg
    



def sort_by_attr(seq,attr):
    intermed = [ (getattr(seq[i],attr), i, seq[i]) for i in xrange(len(seq)) ]
    intermed.sort()
    intermed.reverse() # ranked from greatest to least
    return [ tup[-1] for tup in intermed ]



def jsonp(callback, html):
    html = html.replace('\r\n','').replace("\n", "").replace("'", "&rsquo;");
    return callback + "('" + html + "');"

def compress(data):
    import gzip 
    import cStringIO
    zbuf = cStringIO.StringIO()
    zfile = gzip.GzipFile(mode='wb', compresslevel=2, fileobj=zbuf)
    zfile.write(data)
    zfile.close()
    return zbuf.getvalue()



def minify(js):
		from StringIO import StringIO
		from js.jsmin import JavascriptMinify
		ins = StringIO(js)
		outs = StringIO()
		JavascriptMinify().minify(ins, outs)   
		str = outs.getvalue()
		if len(str) > 0 and str[0] == '\n':
			str = str[1:]
		return str #compress(str)




def css_minify(css):
		return css.replace("\n", "")
		


