from google.appengine.ext import db
from google.appengine.api import users
import logging
from proficiency import Proficiency
import quiz



class Employer(db.Model):
    unique_identifier = db.StringProperty(required=False) # should be soon...
    email = db.EmailProperty(required=False)
    name = db.StringProperty()
    proficiencies = db.StringListProperty() 



class AutoPledge(db.Model):
    employer = db.ReferenceProperty(Employer,
                                    required=True, collection_name='auto_pledges')
    count = db.IntegerProperty(required=True) #  number of autopledges yet.                                   
    proficiency = db.ReferenceProperty(Proficiency,
                                    required=True, collection_name='auto_pledges')
                                    
                                   #TODO: package?
                                    
    # Put BP down 5000 for Automotive Industry. Then give out pledges as people take tests.                             
