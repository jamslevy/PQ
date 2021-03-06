from model.quiz import QuizItem, ItemScore
from model.user import QuizTaker
from .model.proficiency import Proficiency, ProficiencyTopic
from .model.employer import Employer 
from .utils.utils import tpl_path, ROOT_PATH, raise_error
from utils import simplejson
from google.appengine.ext import db
from utils.gql_encoder import GqlEncoder, encode
import logging


     
     
class DataMethods():
	

  def create_business_account(self, uid, email, proficiencies=False, batch=False):
    from accounts.methods import register_account, register_user
    import string
    try:
        int(uid[0]) #check to see if it starts with an integer
        uid = "pq" + uid
    except ValueError: pass #doesnt start with integer	
    fullname = string.capwords(uid.replace("_", " "))
    business_employer = self.register_employer(uid, fullname, email, proficiencies, save=False)
    if not business_employer: return () # already registered
    business_account = register_account(uid, fullname, save=False)
    business_profile = register_user(uid, fullname, fullname, email, is_sponsor=True, save=False)
    if business_profile.is_sponsor is False: return "ERROR"
    if not batch: #only one account being made
        db.put([business_account, business_profile, business_employer])
        self.refresh_employer_images([business_employer])
    return business_account, business_profile, business_employer 


  def register_employer(self, business_name, fullname, email, proficiencies=False, save=True):
	  if Employer.get_by_key_name(business_name): return False
	  print "registering employer: ", business_name
	  new_employer = Employer.get_or_insert(key_name=business_name, unique_identifier = business_name, name = fullname, email=email)
	  if not new_employer.quiz_subjects: 
	  	if proficiencies: new_employer.quiz_subjects = proficiencies
	  if save: db.put(new_employer)
	  return new_employer

  def delete_employer_images(self):
		delete_list = []
		from model.user import Profile, ProfilePicture
		for e in Employer.all().fetch(1000):
			try:  
				this_profile = Profile.get_by_key_name(e.unique_identifier)
				if this_profile.photo.type != "pq": delete_list.append(this_profile.photo)
			except: pass 	
		db.delete(delete_list)	
		
  def refresh_employer_images(self, employer_list=False):
        #TODO: Reduce multiple writes
		from google.appengine.api import images
		save_profiles = []
		from model.user import Profile, ProfilePicture
		if not employer_list: employers = Employer.all().fetch(1000)
		else: employers = employer_list
		logging.info('saving employer images for %s', employers)
		for e in employers:
			p_path = ROOT_PATH + "/data/img/business/"
			try: image_file = open(p_path + str(e.unique_identifier) + ".png")
			except: continue
			image = image_file.read()
			small_image = images.resize(image, 45, 45)
			large_image = images.resize(image, 95, 95)
			new_image = ProfilePicture(small_image = small_image,
									 large_image = large_image,
									 type = "employer"
									 )
			new_image.put()
			logging.info('saved employer image for %s', e.unique_identifier)
			this_profile = Profile.get_by_key_name(e.unique_identifier)
			try:this_profile.photo = new_image
			except:
				logging.info('unable to refresh employer image for %s', e.unique_identifier)
				continue
			save_profiles.append(this_profile)
		logging.info('refreshed %d employer images', len(save_profiles))
		if save_profiles: print "refreshed employer images for", [p.unique_identifier for p in save_profiles]
		db.put(save_profiles)
			
