from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi	#Common Gateway Interface
import cgitb	#adding error logs on the browser (debug).
cgitb.enable()

# Operations with databases:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

import glob
import re

from urllib.parse import parse_qs

from HTMLHelper import HTMLDocument, HTMLTag


#connect and create a session for the database:
engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()



	



# Handler class code: indicates what code to execute based on the type of HTTP request that is sent to the server.
# Problems with these methods:
# 1. only endings of paths are checked, so a/b/c/d and b/c/d may be treated equally.
# 2. when using CRUD, we don´t always check that the result actually exists. should be done:
#	res = session.query(...)
#	if res != []:
# 3. try to use aPath = self.path.split("/") at the beginning and base all IFs on that, instead of endswith.
class WebServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith("/restaurants"):
			#[CRUD - Read] retrieve all the restaurant names from the db:
			items = session.query(Restaurant).all()
			
			#create an empty html document:
			htmlDoc = HTMLDocument()
			
			#add a link to another page which allow to create a new restaurant:
			htmlDoc.addInBody(
				HTMLTag.a("Make a new restaurant here!",
					HTMLTag.attribs(href="/restaurants/new")
				)
			)
			htmlDoc.addInBody(HTMLTag.br(3))
			
			#add the current restaurants to the html:
			for item in items:
				htmlDoc.addInBody(HTMLTag.h3(item.name))
				htmlDoc.addInBody(HTMLTag.a("Edit", HTMLTag.attribs(href="/restaurants/{}/edit".format(item.id))))
				htmlDoc.addInBody(HTMLTag.br())
				htmlDoc.addInBody(HTMLTag.a("Delete", HTMLTag.attribs(href="/restaurants/{}/delete".format(item.id))))
				htmlDoc.addInBody(HTMLTag.br(2))
			
			#output the html created
			self.send_response(200)
			self.send_header('Content-type', 'text/html; charset=utf-8')
			self.end_headers()
			self.wfile.write(htmlDoc.getHTML().encode('utf-8'))
			
		elif self.path.endswith("/restaurants/new"):
			#create the form to display:
			htmlDoc = HTMLDocument()
			htmlDoc.addInBody(HTMLTag.h1("Make a new Restaurant"))
			htmlDoc.addInBody(
				HTMLTag.form(
					HTMLTag.attribs(
						method="POST",
						action="/restaurants/new"),
					HTMLTag.input(HTMLTag.attribs(name="restName", type="text", placeholder = "New Restaurant Name")),
					HTMLTag.input(HTMLTag.attribs(type="submit", value="Submit"))
				)
			)
			
			#create the response and output the html created with it
			self.send_response(200)
			self.send_header('Content-type', 'text/html; charset=utf-8')
			self.end_headers()
			self.wfile.write(htmlDoc.getHTML().encode())
			
		elif self.path.endswith("/edit"):
			pathElems = self.path.split("/")		#/restaurants/<id>/edit
			if pathElems[-3] == "restaurants":
				#lets see if there is an existing restaurant with that id.
				aRest = session.query(Restaurant).filter_by(id=pathElems[-2]).one()
				if aRest != []:
					#create the form to display:
					htmlDoc = HTMLDocument()
					htmlDoc.addInBody(HTMLTag.h1("Edit '{}'".format(aRest.name)))
					htmlDoc.addInBody(
						HTMLTag.form(
							HTMLTag.attribs(
								method="POST"),
							HTMLTag.input(HTMLTag.attribs(name="newName", type="text", placeholder = "New Name")),
							HTMLTag.input(HTMLTag.attribs(type="submit", value="Modify"))
						)
					)
					
					#create the response and output the html created with it
					self.send_response(200)
					self.send_header('Content-type', 'text/html; charset=utf-8')
					self.end_headers()
					self.wfile.write(htmlDoc.getHTML().encode())
					return
				else:
					self.send_header('Location', '/404')
		
		elif self.path.endswith("/delete"):
			pathElems = self.path.split("/")		#/restaurants/<id>/delete
			if pathElems[-3] == "restaurants":
				#lets see if there is an existing restaurant with that id.
				aRest = session.query(Restaurant).filter_by(id=pathElems[-2]).one()
				if aRest != []:
					#create the form to display:
					htmlDoc = HTMLDocument()
					htmlDoc.addInBody(HTMLTag.h1("Do you really want to delete '{}'?".format(aRest.name)))
					htmlDoc.addInBody(
						HTMLTag.form(
							HTMLTag.attribs(method="POST"),
							HTMLTag.input(HTMLTag.attribs(type="submit", value="Delete"))
						)
					)
					
					#create the response and output the html created with it
					self.send_response(200)
					self.send_header('Content-type', 'text/html; charset=utf-8')
					self.end_headers()
					self.wfile.write(htmlDoc.getHTML().encode())
					return
				else:
					self.send_header('Location', '/404')
		
		elif self.path.endswith("/404"):
			htmlDoc = HTMLDocument()
			htmlDoc.addInBody(HTMLTag.h1("404 Not Found!"))
			
			self.send_response(404)
			self.send_header('Content-type', 'text/html; charset=utf-8')
			self.end_headers()
			self.wfile.write(htmlDoc.getHTML().encode())
			
		return	
			
		#except IOError:
		#	self.send_error(404, "File Not Found {}".format(self.path))
			
	def do_POST(self):
		if self.path.endswith("/restaurants/new"):
			# How long was the message?
			length = int(self.headers.get('Content-length', 0))
			
			# Read and parse the message
			data = self.rfile.read(length).decode()
			message = parse_qs(data)["restName"]

			#[CRUD - Create] Add the new restaurant to the database:
			newRestaurant = Restaurant(name = message[0])
			session.add(newRestaurant)
			session.commit()
				
			#Create the response.
			self.send_response(301)
			self.send_header('Content-type', 'text/html')
			self.send_header('Location', '/restaurants')
			self.end_headers()
			
		elif self.path.endswith("/edit"):
			pathElems = self.path.split("/")		#/restaurants/<id>/edit
			if pathElems[-3] == "restaurants":
				# How long was the message?
				length = int(self.headers.get('Content-length', 0))
				
				# Read and parse the message
				data = self.rfile.read(length).decode()
				aNewName = parse_qs(data)["newName"][0]

				#retrieve restaurant id
				restId = self.path.split("/")[-2]
				
				#[CRUD - Update] Modify the restaurant's name on the database:
				aRest = session.query(Restaurant).filter_by(id=restId).one()
				if aRest != []:
					aRest.name = aNewName
					session.add(aRest)
					session.commit()
					
					#Create the response.
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

		elif self.path.endswith("/delete"):
			pathElems = self.path.split("/")		#/restaurants/<id>/delete
			if pathElems[-3] == "restaurants":
				#no need to retrieve any user-input data in this case.
				
				#retrieve restaurant id
				restId = self.path.split("/")[-2]
				
				#[CRUD - Delete] Delete restaurant from the database:
				aRest = session.query(Restaurant).filter_by(id=restId).one()
				if aRest != []:
					session.delete(aRest)
					session.commit()
					
					#Create the response.
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

		
				
# Start-up code: we instantiate our server and specify what port it will listen on.
def main():
	try:
		# Run server
		port = 8080
		httpserver = HTTPServer(('', port), WebServerHandler)
		print("Web server running on port {}".format(port))
		httpserver.serve_forever()
	except KeyboardInterrupt:
		print("^C entered, stopping web server...")
		httpserver.socket.close()
	httpserver.socket.close()

if __name__ == '__main__':
	main()