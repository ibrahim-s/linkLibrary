#installTasks.py
# Copyright 2019-2020 Ibrahim Hamadeh , released under GPL2.0
# required to establish the addon data directory on install, and if previous versions found preserve ini file for available paths.

import os
import wx
import gui
import shutil
from logHandler import log

def onInstall():
	# Retreaving path.ini file from previous installation if exists.
	src= os.path.join(os.path.dirname(__file__), '..', 'linkLibrary', 'availablePaths')
	dest= os.path.join(os.path.dirname(__file__), 'availablePaths')
	if os.path.exists(src):
		try:
			shutil.copytree(src, dest)
		except: pass
		return
		#We returned for if there is a previous installation or version of the addon the user has already choosed a default path for data files and there is no need for next dialog or step.

	# Option to create folder to store addon's library files, if the user is installing the addon for the first time.
	userPath= os.path.expanduser('~')
	addon_data_path= os.path.join(userPath, "linkLibrary-addonFiles")
	if not os.path.exists(addon_data_path):
		# Translators: message asking the user if he wants to decline creating the data folder in the home user directory.
		if gui.messageBox(_("Creating folder to store data files in home user directory ...\n"
		"You can press on Cancel button to skipt this, and adjust this later from the addon's settings dialog,"
		"Do you wants to proceed in creating the addons data folder in your home user directory?"),
		# Translators: Title of message box
		"Information",
		style= wx.OK|wx.CANCEL|wx.ICON_QUESTION)== wx.CANCEL:
			return
		try:
			os.mkdir(addon_data_path)
			#create one file in the directory named general.pickle
			open(os.path.join(addon_data_path, "general.pickle"), 'w').close()
		except Exception as e:
			raise e