from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi	#Common Gateway Interface

# Handler class code: indicates what code to execute based on the type of HTTP request that is sent to the server.
class WebServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/hello"):
				#Create the response.
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				#Include content to send back to the client.
				output = ""
				output += "<html><body><h1>Hello!</h1>"
				output += """
						<form method='POST' enctype='multipart/form-data' action='/hello'>
							<h2>What would you like me to say?</h2>
							<input name='message' type='text'>
							<input type='submit' value='Submit'>
						</form>"""
				output += "</body></html>"
				self.wfile.write(output)
				print(output)
				return
				
			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				
				output = ""
				output += "<html><body><h1>&#161 Hola!</h1>"
				output += """
						<form method='POST' enctype='multipart/form-data' action='/hello'>
							<h2>What would you like me to say?</h2>
							<input name='message' type='text'>
							<input type='submit' value='Submit'>
						</form>"""
				output += "</body></html>"
				self.wfile.write(output)
				print(output)
				return
		except IOError:
			self.send_error(404, "File Not Found {}".format(self.path))
			
	def do_POST(self):
		try:
			#Create the response.
			self.send_response(301)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			
			#Get the content sent from the client and create content based on that.
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('message')
				
			output = ""
			output += "<html><body>"
			output += "<h2>Okay, how about this:</h2> <h1>{}</h1>".format(messagecontent[0])
			output += """
					<form method='POST' enctype='multipart/form-data' action='/hello'>
						<h2>What would you like me to say?</h2>
						<input name="message" type="text">
						<input type="submit" value="Submit">
					</form>"""
			output += "</body></html>"
			self.wfile.write(output)
			print(output)
		except:
			pass


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

if __name__ == '__main__':
	main()