#for compatibility with python3
try:
	import cPickle as pickle
except ImportError:
	import pickle

#.decode("mbcs")
from logHandler import log
import os

CURRENT_DIR= os.path.dirname(__file__).decode("mbcs")
#SAVING_DIR= os.path.join(CURRENT_DIR, "..", "..", "linkLibrary-addonFiles")
SAVING_DIR= os.path.join(os.path.expanduser('~'), 'linkLibrary-addonFiles')

class Link(object):
	#links in a specific library or file
	myLinks={}
	filename= ""

	def __init__(self, url, label, about):
		super(Link, self).__init__()
		self.url= url
		self.label= label
		self.about= about

	@classmethod
	def add_link(cls, url, label, about):
		'''Adding a link to a library.'''
		link= cls(url, label, about)
		cls.myLinks[link.url]= {"label": link.label, "about": link.about}
		log.info( cls.myLinks)
		#cls.save_to_file()

	@classmethod
	def remove_link(cls, url):
		'''removing a link given the link key which is the sourceUrl.'''
		del cls.myLinks[url]
		if not cls.myLinks:
			cls.save_to_file()

	@classmethod
	def remove_allLinks(cls):
		''' Removing all links from a library.'''
		if not cls.myLinks:
			return
		cls.myLinks.clear()
		cls.save_to_file()

	@classmethod
	def save_to_file(cls):
		with open(os.path.join(SAVING_DIR, cls.filename), 'wb') as f:
			pickle.dump(cls.myLinks, f)
		cls.myLinks= {}

	@classmethod
	def retreave_from_file(cls):
		if cls.myLinks: return
		else:
			try:
				with open(os.path.join(SAVING_DIR, cls.filename), 'rb') as f:
					d= pickle.load(f)
					cls.myLinks= d
			except:
				cls.myLinks= {}

	@classmethod
	def getLinkByUrl(cls, url):
		'''make a link object given itss key or sourceUrl'''
		if url in cls.myLinks:
			link= cls(url, cls.myLinks[url]['label'], cls.myLinks[url]['about'])
			return link

	@classmethod
	def getLinkByLabel(cls, label):
		#try:
		url= [key for key in cls.myLinks if cls.myLinks[key]['label']== label]
		if url:
			link=cls.getLinkByUrl(url[0])
			return link

if __name__== '__main__':
	#Book.add_book('book1', 'author1', 'about1', 'size1', 'url1', 'url2')
	#Book.save_to_file()
	Book.retreave_from_file('test.pickle')
	print Book.myBooks
"""
	@classmethod
	def getBookByUrl(cls, url):
		key= [key for key in cls.myBooks if cls.myBooks[key]['url']== url]
		if key:
			book= cls.getBookByKey(key[0])
			return book

	@classmethod
	def getBookByUrl2(cls, url):
		key= [key for key in cls.myBooks if cls.myBooks[key]['url2']== url]
		if key:
			book= cls.getBookByKey(key[0])
			return book
"""