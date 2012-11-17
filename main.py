#!/usr/bin/env python
#
# Copyright 2010 deostroll.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import datetime
import webapp2
import os
import time

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
from django.utils import simplejson

class Grams(db.Model):
	author = db.StringProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

path = os.path.join(os.path.dirname(__file__), 'main.htm')

class entry:
	def __init__(self, x):
		self.author = x.author
		self.content = x.content 
		self.date = str(x.date.date())
		self.time = str(x.date.time())
		self.id = str(x.key())
		self.timestamp = time.mktime(x.date.timetuple())
		
class MainPage(webapp2.RequestHandler):
  def get(self):
		template_vals = {}
		entries = db.GqlQuery("SELECT * FROM Grams ORDER BY __key__ DESC LIMIT 5")
		resp = [entry(x) for x in entries]		
		template_vals['grams'] = resp
		template_vals['lastID'] = str(resp[0].id) if len(resp) > 0 else ''
		self.response.out.write(template.render(path, template_vals))

class ShoutBook(webapp2.RequestHandler):
	
	def post(self):
		greeting = Grams()
		greeting.author = self.request.get('username')
		greeting.content = self.request.get('content')
		greeting.put()
		self.response.headers['Content-Type'] = 'application/json'
		x = greeting
		resp = {
			'author': x.author,
			'date': str(x.date.date()),
			'time': str(x.date.time()),
			'timestamp': time.mktime(x.date.timetuple()),
			'content': x.content,
			'id': str(x.key()) 
			}
		
		self.response.out.write(simplejson.dumps([resp]))
		
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		lastID = self.request.get('last_id')
		resp = None
		noLastIDPresent = len(lastID) == 0
		if noLastIDPresent:
			#query for last 5 requests
			entries = db.GqlQuery("SELECT * FROM Grams ORDER BY __key__ DESC LIMIT 5")
		else:
			entries = db.GqlQuery("SELECT * FROM Grams WHERE __key__ > KEY('%s') ORDER BY __key__ DESC LIMIT 5" % lastID)
		
		if entries.count() == 0:
			resp = []
		else:
			resp = [ {
				'author': x.author,
				'date': str(x.date.date()),
				'time': str(x.date.time()),
				'timestamp': time.mktime(x.date.timetuple()),
				'content': x.content,
				'id': str(x.key()) } for x in entries ]
			
		self.response.out.write(simplejson.dumps(resp))
		
class test(webapp2.RequestHandler):
	def get(self):
		r = self.response.out
		r.write('helloworld')
		r.write('<br/>')
		r.write(self.request.get('id'))
		r.write('<br/>')
		r.write('Actual query string: ' + self.request.query_string) 

class clear(webapp2.RequestHandler):
	def get(self):
		entries = Grams().all();
		for x in entries:
			x.delete();
		self.response.headers['Content-Type'] = 'text/html'
		self.redirect('/')

class add(webapp2.RequestHandler):
	def get(self):
		addrow('person ab 1', 'this is the first message')
		addrow('person ab 2', 'this is the second message')
		addrow('person ab 3', 'this is the third message')
		addrow('person ab 4', 'this is the fourth message')
		addrow('person ab 5', 'this is the fifth message')
		addrow('person ab 6', 'this is the sixth message')		
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write('<p>Entries added</p>')
		self.response.out.write('<a href="/clear">Delete all records</a><br\>')
		self.response.out.write('<a href="/">Home</a><br\>')
		
def addrow(name, content):
    t = Grams()
    t.author = name
    t.content = content
    t.put()




app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/shouts', ShoutBook),
  ('/test', test),
  ('/clear', clear),
  ('/add', add)
  
], debug=True)

