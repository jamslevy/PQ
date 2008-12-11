import logging
# Log a message each time this module get loaded.
logging.info('Loading %s', __name__)
import cgi
import wsgiref.handlers
import datetime, time
from utils.webapp import template
from utils.webapp.util import login_required
from google.appengine.ext import db
from utils import webapp
from utils.utils import ROOT_PATH, tpl_path, memoize
from utils.random import sort_by_attr
from .model.user import Profile, QuizTaker, ProfilePicture




# Template paths
PROFILE_PATH = 'profile/'
REPORT_CARD_LIMIT = 5
CLOUD_LIMIT = 9

class ViewProfile(webapp.RequestHandler):
  #View a profile
  def get(self):
    template_values = self.get_profile()
    if not template_values: return
    path = tpl_path(PROFILE_PATH +'profile_template.html')
    self.response.out.write(template.render(path, template_values))


  def get_profile(self):
		profile_path = self.request.path.split('/profile/')[1].lower()
		profile_path = profile_path.replace(' ','_')
		import urllib
		user = Profile.gql('WHERE profile_path = :1', urllib.unquote(self.request.path.split('/profile/')[1].lower()))
		try:
			user = user.get()
			this_user = user.unique_identifier
		except:
		    self.redirect('/profile_not_found/') # if no user is found
		    return
		profile_owner = False
		if self.session['user']:
		    if user.unique_identifier == self.session['user'].unique_identifier: profile_owner = True
		qt = QuizTaker.get_by_key_name(user.unique_identifier)
		topic_levels = self.get_topic_levels(qt)
		level_cloud = self.make_cloud(topic_levels[0:CLOUD_LIMIT])
		range = 50
		depth = 50
		from model.account import Award, Sponsorship
		return {'user': user, 'profile_owner': profile_owner, 
		        'top_levels': topic_levels[0:REPORT_CARD_LIMIT], 'level_cloud': level_cloud,
		        'range': range, 'depth': depth }


      
  def get_topic_levels(self, qt):
      topic_levels = qt.topic_levels.fetch(100)
      return sort_by_attr(topic_levels, 'topic_level') # sort from greatest to least

      
  def make_cloud(self, topic_levels):
	level_cloud = []
	num = len(topic_levels)
	for tl in topic_levels:
		for n in range(num):
		   level_cloud.append(tl)
		num -= 1
	return level_cloud            


class EditProfile(webapp.RequestHandler):
  @login_required
  def get(self):
    public_photos = self.public_photos()
    if self.session['create_profile'] == True:
        edit_type = "Create"
        self.session['create_profile'] = False
    else: edit_type = 'Edit'
    template_values = {'user': self.session['user'], 'edit_type': edit_type, 
                       'photo_keys': public_photos, 'no_load': True}
    path = tpl_path(PROFILE_PATH +'edit.html')
    self.response.out.write(template.render(path, template_values))

  def public_photos(self):
      public_photos = []
      photos = ProfilePicture.gql("WHERE type = :1", "pq").fetch(10)
      for p in photos:
          public_photos.append(str(p.key()))
      return public_photos


  
      

class ViewEmployerProfile(webapp.RequestHandler):
  def get(self):
    template_values = {}
    path = tpl_path(PROFILE_PATH +'employer_prototype.html')
    self.response.out.write(template.render(path, template_values))
    


class BrowseProfiles(webapp.RequestHandler):
  def get(self):
    template_values = {}
    path = tpl_path(PROFILE_PATH +'browse_profiles.html')
    self.response.out.write(template.render(path, template_values))
    


class LoadUserProfile(webapp.RequestHandler):
  def get(self):
    if not self.request.get('user'): return False
    template_values = {}
    path = tpl_path(PROFILE_PATH + self.request.get('user') + '.html')
    self.response.out.write(template.render(path, template_values))
    







class PreviewViewProfile(webapp.RequestHandler):
  def get(self):

    template_values = {}
    path = tpl_path(PROFILE_PATH +'prototype.html')
    self.response.out.write(template.render(path, template_values))





class Image (webapp.RequestHandler):  # TODO: Memoize This!

  @memoize('image_object')
  def get(self):
    image_type = self.request.path.split('/image/')[1].lower().replace('/','')
    if image_type == 'profile': return self.profile_image()
    if image_type == 'subject': return self.subject_image()

  def profile_image(self):      
    if not self.request.get("img_id"): 
        self.redirect('/picture_not_found')
        return
    try: 
        pic = ProfilePicture.get(self.request.get("img_id"))
        self.response.headers['Content-Type'] = "image/png"
        if self.request.get("size") == "large": self.response.out.write(pic.large_image)
        else: self.response.out.write(pic.small_image)
    except: 
        self.redirect('/picture_not_found')
        return
    
          
  def subject_image(self):      
    from model.proficiency import SubjectImage
    if not self.request.get("img_id"): 
        self.redirect('/picture_not_found')
        return
    try: 
        pic = SubjectImage.get(self.request.get("img_id"))
        self.response.headers['Content-Type'] = "image/png"
        if self.request.get("size") == "large": self.response.out.write(pic.large_image)
        else: self.response.out.write(pic.small_image)
    except: 
        self.redirect('/picture_not_found')
        return
    

