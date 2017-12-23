from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi	#Common Gateway Interface
import cgitb	#adding error logs on the browser (debug).
cgitb.enable()

# Operations with databases:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem



from urllib.parse import parse_qs


#connect and create a session for the database:
engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class HTMLDocument:
	"""This can be extended to suport all the tags and parameters.
	
	something like: addInBody(self, h1(content))
	or even: addInBody(self, h1(content, id="aId", name="aName"))"""
	def __init__(self):
		self._html = "<html><head>{}</head><body>{}</body></html>"
		
	def addInHead(self, str):
		self._html = self._html.format(str+"{}", "{}")
		
	def addInBody(self, str):
		self._html = self._html.format("{}", str+"{}")
		
	def getHTML(self):
		return self._html.format("", "")
	
	def h1(str):
		return "<h1>" + str + "</h1>"
		
	def h3(str):
		return "<h3>" + str + "</h3>"
		
	def a(str, attrs):
		return "<a {}>".format(attrs) + str + "</a>"

	def attribs(**attrs):
		"""Helper method to add attributes in every tag that supports it."""
		s = ""
		for k in attrs:
			s += " " + k + "='" + attrs[k] + "'"
		return s
		
	def br(n=1):
		return "<br>" * n
	
	def input(attrs = ""):
		return "<input{}>".format(attrs)
	
	def textarea(attrs = ""):
		return "<textarea{}></textarea>".format(attrs)		
	
	def form(attrs, *subtags):
		s = "<form{}>".format(attrs)
		for tag in subtags:
			s += tag
		s += "</form>"
		return s
	



# Handler class code: indicates what code to execute based on the type of HTTP request that is sent to the server.
class WebServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith("/restaurants"):
			#retrieve all the restaurant names from the db:
			items = session.query(Restaurant).all()
			
			#create an empty html document:
			htmlDoc = HTMLDocument()
			
			#add a link to another page which allow to create a new restaurant:
			htmlDoc.addInBody(
				HTMLDocument.a("Make a new restaurant here!",
					HTMLDocument.attribs(href="/restaurants/new")
				)
			)
			htmlDoc.addInBody(HTMLDocument.br(3))
			
			#add the current restaurants to the html:
			for item in items:
				htmlDoc.addInBody(HTMLDocument.h3(item.name))
				htmlDoc.addInBody(HTMLDocument.a("Edit", HTMLDocument.attribs(href="#")))
				htmlDoc.addInBody(HTMLDocument.br())
				htmlDoc.addInBody(HTMLDocument.a("Delete", HTMLDocument.attribs(href="#")))
				htmlDoc.addInBody(HTMLDocument.br(2))
			
			#output the html created
			self.send_response(200)
			self.send_header('Content-type', 'text/html; charset=utf-8')
			self.end_headers()
			self.wfile.write(htmlDoc.getHTML().encode('utf-8'))
			return
			
		if self.path.endswith("/restaurants/new"):
			#create the form to display:
			htmlDoc = HTMLDocument()
			htmlDoc.addInBody(HTMLDocument.h1("Make a new Restaurant"))
			htmlDoc.addInBody(
				HTMLDocument.form(
					HTMLDocument.attribs(
						method="POST",
						action="/restaurants/new"),
					HTMLDocument.textarea(HTMLDocument.attribs(name="restName", type="text")),
					HTMLDocument.input(HTMLDocument.attribs(type="submit", value="Submit"))
				)
			)
			
			#to remove, and all it s references:
			output = "<html><head></head><body><h1>add rest</h1><form method='POST' action='/restaurants/new'><textarea name='restName' type='text'></textarea><input type='submit' value='Submit'></form></body></html>"
			
			print("output:\n" + output)
			print("htmlDoc:\n" + htmlDoc.getHTML())
			
			#create the response and output the html created with it
			self.send_response(200)
			self.send_header('Content-type', 'text/html; charset=utf-8')
			self.end_headers()
			self.wfile.write(htmlDoc.getHTML().encode())
			#self.wfile.write(output.encode())
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

			#Add the new restaurant to the database:
			newRestaurant = Restaurant(name = message[0])
			session.add(newRestaurant)
			session.commit()
				
			#Create the response.
			self.send_response(301)
			self.send_header('Content-type', 'text/html')
			self.send_header('Location', '/restaurants')
			self.end_headers()
			return
				
				
#			output = ""
#			output += "<html><body>"
#			output += "<h2>Okay, how about this:</h2> <h1>{}</h1>".format(messagecontent[0])
#			output += """
#					<form method='POST' enctype='multipart/form-data' action='/hello'>
#						<h2>What would you like me to say?</h2>
#						<input name="message" type="text">
#						<input type="submit" value="Submit">
#					</form>"""
#			output += "</body></html>"
#			self.wfile.write(output)
#			print(output)


# Main code: we instantiate our server and specify what port it will listen on.

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