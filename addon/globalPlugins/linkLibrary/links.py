# -*- coding: UTF-8 -*-
#links.py
# Copyright 2019 ibrahim hamadeh, released under GPLv2.0
# See the file COPYING for more details
#This module is aimed to construct link object, retreave links from file, save links to file and use other helpful functions.

import wx, gui
import os
import json
from logHandler import log

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
		'''Saving links in a specific library to file'''
		try:
			with open(os.path.join(cls.SAVING_DIR, cls.filename), 'w', encoding= 'utf-8') as f:
				json.dump(cls.myLinks, f, ensure_ascii= False, indent= 4)
			cls.myLinks= {}
		except Exception as e:
#			log.info("Error saving links to file",exc_info=1)
			raise e
			return

	@classmethod
	def retreave_from_file(cls):
		'''Retreaving links from a specific library file.'''
		if cls.myLinks: 
			return
		try:
			with open(os.path.join(cls.SAVING_DIR, cls.filename), encoding= 'utf-8') as f:
				d= json.load(f)
				cls.myLinks= d
		#except EOFError:
			#cls.myLinks= {}
			#return
		except Exception as e:
			# Translators: Message displayed when getting an error trying to retreave link data
			gui.messageBox(_("Unable to load links data"), 
			# Translators: Title of message box
			_("Error"), wx.OK|wx.ICON_ERROR)
			raise e

	@classmethod
	def getLinkByUrl(cls, url):
		'''make a link object given itss key or sourceUrl'''
		if url in cls.myLinks:
			link= cls(url, cls.myLinks[url]['label'], cls.myLinks[url]['about'])
			return link

	@classmethod
	def getLinkByLabel(cls, label):
		'''Getting the link object given its label'''
		#try:
		url= [key for key in cls.myLinks if cls.myLinks[key]['label']== label]
		if url:
			link=cls.getLinkByUrl(url[0])
			return link
