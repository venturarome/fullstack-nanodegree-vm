class HTMLDocument:
	"""Creates and formats a basic but extensible HTML structure.
	
	Its base structure is:
	<html>
	<head></head>
	<body></body>
	<html>
	and lets add content inside the <head> and <body> tags."""
	def __init__(self):
		self._html = "<html><head>{}</head><body>{}</body></html>"
		
	def addInHead(self, str):
		self._html = self._html.format(str+"{}", "{}")
		
	def addInBody(self, str):
		self._html = self._html.format("{}", str+"{}")
		
	def getHTML(self):
		return self._html.format("", "")
	
		
class HTMLTag:
	"""Defines methods to create HTML tags."""
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