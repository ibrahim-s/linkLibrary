# -*- coding: UTF-8 -*-
# links.py
# Copyright 2019 ibrahim hamadeh, released under GPLv2.0
# See the file COPYING for more details
# This module is aimed to construct link object, retreave links from file, save links to file and use other helpful functions.

import wx, gui
import os
import json
from logHandler import log

class Link(object):
	'''Class to create the link object, given the url, label, and about for the link.'''
	myLinks={}
	sublibraryLinks = {}
	SAVING_DEFAULT_DIR= "" # it will take a value when addon loads, sent from __init__.py
	SAVING_DIR= SAVING_DEFAULT_DIR
	sublibraries_path= None
	filename= ""
	isSublibrary= False

	def __init__(self, url, label, about):
		super(Link, self).__init__()
		self.url= url
		self.label= label
		self.about= about

	@classmethod
	def changeClassAttributes(cls, default= True):
		if default:
			cls.SAVING_DIR= cls.SAVING_DEFAULT_DIR
			cls.sublibraries_path= None
			cls.isSublibrary= False
		else:
			cls.SAVING_DIR= cls.sublibraries_path

	@classmethod
	def add_link(cls, url, label, about):
		'''Adding a link to a library.'''
		#log.info('adding a link to library ...')
		link= cls(url, label, about)
		if not cls.isSublibrary:
			cls.myLinks[link.url]= {"label": link.label, "about": link.about}
		else:
			cls.sublibraryLinks[link.url]= {"label": link.label, "about": link.about}
		#log.info(f'cls.myLinks: {cls.myLinks}')
		#log.info(f'cls.sublibraryLinks: {cls.sublibraryLinks}')

	@classmethod
	def remove_link(cls, url):
		'''removing a link given the link key which is the sourceUrl.'''
		# myLinks is a copy of one of the 2 dictionaries.
		myLinks= cls.myLinks if not cls.isSublibrary else cls.sublibraryLinks
		del myLinks[url]
		if not myLinks:
			cls.save_to_file()

	@classmethod
	def remove_allLinks(cls):
		''' Removing all links from a library.'''
		# myLinks is a copy of one of the 2 dictionaries.
		myLinks= cls.myLinks if not cls.isSublibrary else cls.sublibraryLinks
		if not myLinks:
			return
		myLinks.clear()
		cls.save_to_file()

	@classmethod
	def save_to_file(cls):
		'''Saving links in a specific library to file'''
		#log.info('saving links to file ...')
		#log.info(f'SAVING_DIR= {cls.SAVING_DIR}, filename= {cls.filename}, sublibraries_path= {cls.sublibraries_path}')
		#log.info(f'cls.myLinks:{cls.myLinks}, cls.sublibraryLinks: {cls.sublibraryLinks}')
		try:
			with open(os.path.join(cls.SAVING_DIR, cls.filename), 'w', encoding= 'utf-8') as f:
				if not cls.isSublibrary:
					json.dump(cls.myLinks, f, ensure_ascii= False, indent= 4)
					cls.myLinks= {}
				else:
					json.dump(cls.sublibraryLinks, f, ensure_ascii= False, indent= 4)
					cls.sublibraryLinks= {}

		except Exception as e:
			raise e

	@classmethod
	def retreave_from_file(cls):
		'''Retreaving links from a specific library file.'''
		#log.info('retreaving links from file ...')
		#log.info(f'SAVING_DIR= {cls.SAVING_DIR}, filename= {cls.filename}, sublibraries_path= {cls.sublibraries_path}')
		if not cls.isSublibrary and cls.myLinks: 
			return
		elif cls.isSublibrary and cls.sublibraryLinks:
			return
		try:
			with open(os.path.join(cls.SAVING_DIR, cls.filename), encoding= 'utf-8') as f:
				d= json.load(f)
			if not cls.isSublibrary:
				cls.myLinks= d
			else:
				cls.sublibraryLinks= d
		except Exception as e:
			# Translators: Message displayed when getting an error trying to retreave link data
			gui.messageBox(_("Unable to load links data"), 
			# Translators: Title of message box
			_("Error"), wx.OK|wx.ICON_ERROR)
			raise e

	@classmethod
	def get_linksDictionary(cls):
		if not cls.isSublibrary:
			return cls.myLinks
		else:
			return cls.sublibraryLinks

	@classmethod
	def getLinkByUrl(cls, url):
		'''make a link object given itss key or sourceUrl'''
		my_links= cls.myLinks if not cls.isSublibrary else cls.sublibraryLinks
		if url in my_links:
			link= cls(url, my_links[url]['label'], my_links[url]['about'])
			return link

	@classmethod
	def getLinkByLabel(cls, label):
		'''Getting the link object given its label'''
		myLinks= cls.myLinks if not cls.isSublibrary else cls.sublibraryLinks
		url= [key for key in myLinks if myLinks[key]['label']== label]
		if url:
			link=cls.getLinkByUrl(url[0])
			return link

	def __repr__(self):
		return f'Link(label= {self.label}, url= {self.url})'
