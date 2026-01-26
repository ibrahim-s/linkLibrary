# -*- coding: utf-8 -*-
#linkLibrary
#Copyright 2019 ibrahim hamadeh, released under GPLv2.0
#See the file COPYING for more details.
# An addon that helps collect and arrange and access easily informations related to links under specific categories

import globalPluginHandler 
import core, ui
import wx, gui
import os, sys
import re
import api
import config
import globalVars
import browseMode
import shutil
import json
from scriptHandler import script
from configobj import ConfigObj
from logHandler import log
from .libraryDialog import LibraryDialog
from .linkDialog import LinkDialog, LinkSublibrary

import addonHandler
addonHandler.initTranslation()

# default path of library files for the addon, home user lirectory
homeDirectory= os.path.expanduser('~')

#default configuration 
configspec={
	"chosenDataPath": "string(default='Home user directory')",
	"afterActivatingLink": "integer(default=1)"
}
config.conf.spec["linkLibrary"]= configspec

#path of ini file to store available paths
iniFile= os.path.join(globalVars.appArgs.configPath, "addons", "linkLibrary", "availablePaths", "paths.ini")

#creating ini file for available directories or paths
def createIniFileForAvailablePaths(iniFile):
	#Create parent directory of iniFile if not present
	availablePaths= os.path.join(globalVars.appArgs.configPath, "addons", "linkLibrary", "availablePaths")
	if not os.path.exists(availablePaths):
		os.mkdir(availablePaths)
	configHandle= ConfigObj(iniFile, encoding="UTF-8")
	configHandle["availablePaths"]= {}
	configHandle["availablePaths"]["Home user directory"]= homeDirectory
	configHandle.write()

#create ini file for the first time
if not os.path.exists(iniFile):
	createIniFileForAvailablePaths(iniFile)

#handle of ini file for available paths
pathsHandle=ConfigObj(iniFile, encoding="UTF-8")

def getChosenDataPath():
	'''Gets directory for path chosen by the user.'''
	pathName= config.conf["linkLibrary"]["chosenDataPath"]
	#directory or value for this pathName, as saved in paths.ini file
	try:
		chosenPath= os.path.abspath(pathsHandle["availablePaths"][pathName])
	except KeyError:
		chosenPath= homeDirectory
		# Key not exist in availablePaths, so better remove it from base configuration, and return the value of chosenDataPath to Home user directory
		config.conf["linkLibrary"]["chosenDataPath"]= 'Home user directory'
		# Better save the configuration
		config.conf.save()
		log.info("Error in getting chosenDataPath from availablePaths", exc_info=1)
	finally:
		from .links import Link
		Link.SAVING_DEFAULT_DIR= os.path.join(chosenPath, 'linkLibrary-addonFiles')
		return chosenPath

#initial value when no instance of dialog is opened
LIBRARYDIALOG= None
# Instance of HelperFrame , that contains the popup menu, to add a link on the fly
helperFrameInstance= None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Link Library")

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.makeAddonMenu()

	def makeAddonMenu(self):
		self.preferencesMenu= gui.mainFrame.sysTrayIcon.preferencesMenu
		self.addonMenu= wx.Menu()
		self.subMenu= self.preferencesMenu.AppendSubMenu(self.addonMenu, 
		# Translators: label of submenu.
		_("&Link Library"))
		# Link library settings menu item.
		self.linkLibrarySetting= self.addonMenu.Append(wx.ID_ANY, 
		# Translators: Label of Link Library Setting menu item
		_("Link Library Setting..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onLinkLibrarySetting, self.linkLibrarySetting)
		#open library dialog menu item
		self.openLibraryDialog= self.addonMenu.Append(wx.ID_ANY, 
		# Translators: Label of Open Library Dialog menu item
		_("Open Library Dialog"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onOpenLibraryDialog, self.openLibraryDialog)
		# Copy Library Folder menu item.
		self.copyLibraryFolder= self.addonMenu.Append(wx.ID_ANY,
		# Translators: Label of Copy Library Folder menu item
		_("Copy Library Folder"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCopyLibrariesFolder, self.copyLibraryFolder)
		#Import Library Folder menu item.
		self.importLibraryFolder= self.addonMenu.Append(wx.ID_ANY,
		# Translators: Label of Import Library Folder menu item
		_("Import Library Folder"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onImportLibrariesFolder, self.importLibraryFolder)

	def terminate(self):
		try:
			self.preferencesMenu.Remove(self.subMenu)
		except:
			pass

	def onLinkLibrarySetting(self, evt):
		if hasattr(gui.mainFrame, 'popupSettingsDialog'):
			gui.mainFrame.popupSettingsDialog(LinkDialogSettings)
		else:
			gui.mainFrame._popupSettingsDialog(LinkDialogSettings)

	def onOpenLibraryDialog(self, evt):
		self.script_openLibraryDialog(None)

	def onCopyLibrariesFolder(self, evt):
		gui.mainFrame.prePopup()
		d = CopyDialog(gui.mainFrame)
		d.Show()
		gui.mainFrame.postPopup()

	def onImportLibrariesFolder(self, evt):
		gui.mainFrame.prePopup()
		d = ImportDialog(gui.mainFrame)
		d.Show()
		gui.mainFrame.postPopup()

	@script(
	# Translators: message displayed in input help mode for openning  link library dialog.
	description= _("Open  Link Library dialog."),
	)
	def script_openLibraryDialog(self, gesture):
		if LinkSublibrary.sublibraryInstance:
			LinkSublibrary.sublibraryInstance.Raise()
		elif LinkDialog.currentInstance:
			LinkDialog.currentInstance.Raise()
		else:
			global LIBRARYDIALOG
			if not LIBRARYDIALOG:
				LIBRARYDIALOG= LibraryDialog(gui.mainFrame, getChosenDataPath())
			else:
				LIBRARYDIALOG.Raise()

	@script(
	# Translators: message displayed in input help mode for adding a link on the fly.
	description=_("Add the link and title of web page on the fly to library you choose."),
	)
	def script_addLinkOnTheFly(self, gesture):
		obj = api.getNavigatorObject().treeInterceptor
		if not isinstance(obj, browseMode.BrowseModeTreeInterceptor):
			gesture.send()
			return
		# Send the navigatorObjectTreeInterceptor to HelperFrame, to get link of web page.
		# because when the frame is shown, these properties of web page can not b accessed
		HelperFrame.navigatorObjectTreeInterceptor= obj
		# Send foregroundObject to HelperFrame to get title of web page
		HelperFrame.foregroundObject= api.getForegroundObject()
		def showPopupMenuInFrame():
			global helperFrameInstance
			if not helperFrameInstance:
				f= HelperFrame(gui.mainFrame)
				f.Raise()
				f.Show()
				helperFrameInstance = f
			else:
				helperFrameInstance.Raise()
		wx.CallAfter(showPopupMenuInFrame)

	#Link Library Dialog Settings class
class LinkDialogSettings(gui.SettingsDialog):
	# Translators: title of the dialog
	title= _("Link Library Settings")
	#The dictionary in which we will store in it temporarly the label an value of the new added path
	pathInfoDict= {}

	def makeSettings(self, sizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		self.availablePaths= settingsSizerHelper.addLabeledControl(
		# Translators: label of cumbo box of available paths to contain data files.
		_("Choose Path to store Data Files"), wx.Choice, choices=[key for key in pathsHandle["availablePaths"]])
		#log.info([key for key in pathsHandle["availablePaths"]])
		self.availablePaths.Bind(wx.EVT_CHOICE, self.onAvailablePaths)

		# Translators: label of button to add a new path.
		label= _("Add New Path")
		self.addPathBtn= settingsSizerHelper.addItem( wx.Button(self, -1, label))
		self.addPathBtn.Bind(wx.EVT_BUTTON, self.onAddPath)

		# Translators: label of Remove path button.
		label= _("Remove Selected Path")
		self.removePathBtn= settingsSizerHelper.addItem( wx.Button(self, -1, label))
		self.removePathBtn.Bind(wx.EVT_BUTTON, self.onRemovePath)

		# A combo box, what to do after activating a link.
		options= [
			# Translators: Option in combo box to do nothing
			_("Do nothing"),
			# Translators: Option in combo box to close library window.
			_("Close library window only"),
			# Translators: Option in combo box to close main window of addon.
			_("Close main window of addon")
		]
		self.chooseActionCumbo= settingsSizerHelper.addLabeledControl(
			# Translators: Label of combo box
			_("After activating a link:"), wx.Choice, choices= options)
		self.chooseActionCumbo.SetSelection(config.conf["linkLibrary"]["afterActivatingLink"])

	def postInit(self):
		self.availablePaths.SetStringSelection(config.conf["linkLibrary"]["chosenDataPath"])
		#log.info(config.conf["linkLibrary"]["chosenDataPath"])
		#log.info(self.availablePaths.GetStringSelection())
		if self.availablePaths.GetStringSelection()== "Home user directory":
			#log.info('under if')
			self.removePathBtn.Enabled= False
		self.availablePaths.SetFocus()

	def onAvailablePaths(self, evt):
		state= self.availablePaths.StringSelection != 'Home user directory'
		self.removePathBtn.Enabled= state

	def onAddPath(self, evt):
		gui.mainFrame.prePopup()
		d= AddPathDialog(self)
		d.Show()
		gui.mainFrame.postPopup()

	def onRemovePath(self, evt):
		name= self.availablePaths.GetStringSelection()
		i= self.availablePaths.GetSelection()
		if name and name!= "Home user directory":
			if gui.messageBox(
			# Translators: The confirmation prompt displayed when the user requests to remove the selected path.
			_("This path({}) will be permanently removed. This action cannot be undone.").format(name),
			# Translators: The title of the confirmation dialog for removal of selected path.
			_("Warning"),
			wx.OK | wx.CANCEL | wx.ICON_QUESTION
			) != wx.OK:
				return
			self.Hide()
			self.availablePaths.Delete(i)
			if name== config.conf["linkLibrary"]["chosenDataPath"]:
				#return to default path
				config.conf["linkLibrary"]["chosenDataPath"]= "Home user directory"
			if name in pathsHandle["availablePaths"]:
				del pathsHandle["availablePaths"][name]
			if name in self.pathInfoDict:
				del self.pathInfoDict[name]
			self.postInit()
			self.Show()

	def onOk(self, evt):
		pathName= self.availablePaths.GetStringSelection()
		#log.info(self.pathInfoDict)
		for key, value in self.pathInfoDict.items():
			#if value or directory ends with 'linkLibrary-addonFiles', remove it's base
			if os.path.basename(value)== 'linkLibrary-addonFiles':
				value= os.path.dirname(value)
			#store the addedpaths in the ini file
			pathsHandle["availablePaths"][key]= value
		pathsHandle.write()
		config.conf["linkLibrary"]["chosenDataPath"]= pathName
		config.conf["linkLibrary"]["afterActivatingLink"]= self.chooseActionCumbo.GetSelection() 
		super(LinkDialogSettings, self).onOk(evt)

#Most of stuff here, copy libraries folder dialog and import libraries folder dialog is borrowed from Read Feeds by Noelia.

class PathSelectionWithoutNewDir(gui.guiHelper.PathSelectionHelper):

	def __init__(self, parent, buttonText, browseForDirectoryTitle):
		super(PathSelectionWithoutNewDir, self).__init__(parent, buttonText, browseForDirectoryTitle)

	def onBrowseForDirectory(self, evt):
		startPath = self.getDefaultBrowseForDirectoryPath()
		with wx.DirDialog(self._parent, self._browseForDirectoryTitle, defaultPath=startPath, style=wx.DD_DIR_MUST_EXIST | wx.DD_DEFAULT_STYLE) as d:
			if d.ShowModal() == wx.ID_OK:
				self._textCtrl.Value = d.Path

#Copy Dialog, pops up when pressing on copy libraries folder menu
class CopyDialog(wx.Dialog):
	LIBRARIES_DIR= os.path.join(getChosenDataPath(), 'linkLibrary-addonFiles')

	def __init__(self, parent):
		# Translators: title of Copy Dialog
		super(CopyDialog, self).__init__(parent, title= _("Copy Libraries Folder"))

		mainSizer= wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper( self, wx.VERTICAL)
		# Translators: An informational message displayed in the Copy dialog.
		dialogCaption=_("To copy libraries folder , please select the path and other options and then press Continue")
		sHelper.addItem(wx.StaticText(self, label=dialogCaption))
		# Translators: The label of a grouping containing controls to select the destination directory
		directoryGroupText = _("Destination &directory:")
		groupHelper = sHelper.addItem(gui.guiHelper.BoxSizerHelper(self, sizer=wx.StaticBoxSizer(wx.StaticBox(self, label=directoryGroupText), wx.VERTICAL)))

		# Translators: The label of a button to browse for a directory.
		browseText = _("Browse...")
		# Translators: The title of the dialog presented when browsing for the destination directory 
		dirDialogTitle = _("Select Directory")
		directoryEntryControl = groupHelper.addItem(PathSelectionWithoutNewDir(self, browseText, dirDialogTitle))
		self.directoryEdit = directoryEntryControl.pathControl

		bHelper = sHelper.addDialogDismissButtons(gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		# Translators: Label of continue button
		continueButton = bHelper.addButton(self, label=_("&Continue"), id=wx.ID_OK)
		continueButton.SetDefault()
		continueButton.Bind(wx.EVT_BUTTON, self.onCopyLibrariesFolder)
		bHelper.addButton(self, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)

		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def onCopyLibrariesFolder(self, evt):
		selected_path= self.directoryEdit.Value
		if not selected_path:
			gui.messageBox(
			# Translators: The message displayed when the user has not specified a destination directory
			_("Please specify a directory."),
			# Translators: Title of dialog
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		if not os.path.isdir(selected_path):
			# Translators: The message displayed when the user specifies an invalid destination directory
			gui.messageBox(_("%s is invalid, please select a valid directory path.")%selected_path,
			# Translators: Title of dialog
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		self.Hide()
		self.copyFolder(selected_path)
		self.Destroy()

	def copyFolder(self, destination):
		# to ensure that the removed directory will not be one of the main directories such as documents or music or other important ones
		if not os.path.basename(destination)== 'linkLibrary-addonFiles':
			destination= os.path.join(destination, "linkLibrary-addonFiles")
		try:
			if os.path.exists(destination):
			#if it exists, only linkLibrary-addonFiles folder will be remove, which is the base name of destination path
				shutil.rmtree(destination, ignore_errors=True)
			shutil.copytree(self.LIBRARIES_DIR, destination)
		except Exception as e:
			# Translators: message presented when copy fails
			gui.messageBox(_("Sorry, copying libraries folder did not succeed"),
			#label of dialog
			_("Error"), wx.OK|wx.ICON_ERROR)
			raise e
		else:
			core.callLater(100, ui.message, _("Information:Folder Copied"))

	def onCancel(self, evt):
		self.Destroy()

class ImportDialog(wx.Dialog):
	LIBRARIES_DIR= os.path.join(getChosenDataPath(), 'linkLibrary-addonFiles')

	def __init__(self, parent):
		# Translators: title of import dialog
		super(ImportDialog, self).__init__(parent, title= _("Import Libraries Folder"))

		mainSizer= wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: An informational message displayed in the Import dialog.
		dialogCaption=_("To import libraries folder , please select the path of folder you want to import, and then press Continue")
		sHelper.addItem(wx.StaticText(self, label=dialogCaption))
		# Translators: The label of a grouping containing controls to select the destination directory in the Import dialog.
		directoryGroupText = _("Directory of folder you want to import:")
		groupHelper = sHelper.addItem(gui.guiHelper.BoxSizerHelper(self, sizer=wx.StaticBoxSizer(wx.StaticBox(self, label=directoryGroupText), wx.VERTICAL)))
		# Translators: The label of a button to browse for the required directory.
		browseText = _("Browse...")
		# Translators: The title of the dialog presented when browsing for the directory to be imported.
		dirDialogTitle = _("Select Directory to import")
		directoryEntryControl = groupHelper.addItem(PathSelectionWithoutNewDir(self, browseText, dirDialogTitle))
		self.directoryEdit = directoryEntryControl.pathControl
		bHelper = sHelper.addDialogDismissButtons(gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		continueButton = bHelper.addButton(self, label=_("&Continue"), id=wx.ID_OK)
		continueButton.SetDefault()
		continueButton.Bind(wx.EVT_BUTTON, self.onImportLibrariesFolder)
		
		bHelper.addButton(self, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def onImportLibrariesFolder(self, evt):
		selected_path= self.directoryEdit.Value
		if not selected_path:
			# Translators: Message displayedwhen no directory is specified.
			gui.messageBox(_("Please specify a directory."),
			# Translators: label of dialog
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		if not os.path.isdir(selected_path):
			# Translators: message displayed when path selected is not valid
			gui.messageBox(_("Sorry, but %s is invalid path.")%selected_path,
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		self.Hide()
		self.importFolder(selected_path)
		self.Destroy()

	def importFolder(self, source_directory):
		# If at least one file in the imported folder has a json extension, the folder will be accepted
		# In other words, if not any file is a json file, the folder will be considered unvalid
		if not os.path.basename(source_directory)== "linkLibrary-addonFiles" or not any(os.path.splitext(_file)[-1]== '.json' for _file in os.listdir(source_directory)):
			# Translators: message displayed when folder to be imported not named linkLibrary-addonFiles, or all files in it has not .json extension
			gui.messageBox(_("Check that the folder name is linkLibrary-addonFiles, and all files in it has a .json extension."),
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		# Translators: message to warn the user that the old library folder will be removed.
		if gui.messageBox(_("You should be aware by this import, the old linkLibrary-addonFiles will be removed and replaced by the newly imported one,\n"
		"and this can not be undone, are you sure you want to proceed?"),
		# Translators: Title of message box
		"Warning",
		style= wx.YES|wx.NO|wx.ICON_WARNING)== wx.NO:
			return
		try:
			shutil.rmtree(self.LIBRARIES_DIR, ignore_errors= True)
			shutil.copytree(source_directory, self.LIBRARIES_DIR)
		except Exception as e:
			# Translators: message presented when import folder fails
			gui.messageBox(_("Import libraries folder failed."),
			_("Error"), wx.OK|wx.ICON_ERROR)
			raise e
		else:
			# Translators: message presented when importing libraries folder succeeded.
			core.callLater(100, ui.message, _("Information: Libraries folder imported successfuly."))

	def onCancel(self, evt):
		self.Destroy()

class AddPathDialog(wx.Dialog):
	"""Dialog to add new path for data files."""
	def __init__(self,parent):
		# Translators: Title of dialog.
		title=_("Add new path")
		super(AddPathDialog, self).__init__(parent, title= title)
		self.parent= parent

		mainSizer= wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

				# Translators: The label of a grouping containing controls to select the destination directory in the Add new path dialog.
		directoryGroupText = _("Path of the directory:(c:\\users\\...)")
		groupHelper = sHelper.addItem(gui.guiHelper.BoxSizerHelper(self, sizer=wx.StaticBoxSizer(wx.StaticBox(self, label=directoryGroupText), wx.VERTICAL)))

		# Translators: Label of text control to enter path name.
		label= _("Enter a general name for the path(example dropbox or Documents or any other)")
		self.nameEntry= sHelper.addLabeledControl(label, wx.TextCtrl)
		# Translators: The label of a button to browse for the required directory.
		browseText = _("Browse...")
		# Translators: The title of the dialog presented when browsing for the directory to be imported.
		dirDialogTitle = _("Select Directory")
		directoryEntryControl = groupHelper.addItem(PathSelectionWithoutNewDir(self, browseText, dirDialogTitle))
		self.directoryEdit = directoryEntryControl.pathControl
		bHelper = sHelper.addDialogDismissButtons(gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		okButton = bHelper.addButton(self, label=_("Ok"), id=wx.ID_OK)
		okButton.SetDefault()
		okButton.Bind(wx.EVT_BUTTON, self.onOkButton)
		
		bHelper.addButton(self, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.onCancelButton, id=wx.ID_CANCEL)
		mainSizer.Add(sHelper.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

	def onOkButton(self, evt):
		pathValue= self.directoryEdit.Value
		#log.info(pathValue)
		if not pathValue:
			gui.messageBox(
			# Translators: The message displayed when the user has not specified a directory
			_("Please specify a directory."),
			_("Warning"), wx.OK|wx.ICON_WARNING)
			return
		if not os.path.isdir(pathValue):
			# Translators: message displayed when path selected is not valid
			gui.messageBox(_("Sorry, but %s is invalid path.")%pathValue,
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		if self.nameEntry.Value.strip():
			pathName= self.nameEntry.Value
		else:
			splittedPath= os.path.normpath(pathValue).split(os.sep)
			# last part of path
			baseName= splittedPath[-1]
			pathName= baseName if baseName!= "linkLibrary-addonFiles" else splittedPath[-2]
		#pathName= self.nameEntry.Value or pathValue
		pathName= pathName.strip()
		parent= self.parent
		parent.pathInfoDict[pathName]= pathValue
		parent.availablePaths.Append(pathName)
		parent.availablePaths.SetStringSelection(pathName)
		parent.onAvailablePaths(None)
		#log.info(pathName)
		wx.CallAfter(parent.availablePaths.SetFocus)
		self.Destroy()

	def onCancelButton(self, evt):
		self.Destroy()

class HelperFrame(wx.Frame):
	"""A frame, contains a button, that triggers the popup menu of libraries to add the web page link to one of them.
	"""
	def __init__(self, parent):
		super(HelperFrame, self).__init__(parent, wx.ID_ANY,
		# Translators: title of frame
		title="Add link and title of web page to library",
		size=(300,200))
		# dictionary that tracks submenu ids as keys, and the name of the folder in which they reside as valid.
		self.subMenuId2parent: dict[int, str] = {}
		panel = wx.Panel(self)
		sizer= wx.BoxSizer(wx.VERTICAL)
		self.chooseLibraryButton= wx.Button(panel, wx.ID_ANY,
		# Translators: Label of choose library button
		_("Choose library:"))
		self.chooseLibraryButton.Bind(wx.EVT_BUTTON, self.onChooseLibrary)
		sizer.Add(self.chooseLibraryButton, 0, wx.ALL | wx.CENTER, 20)
		panel.SetSizer(sizer)
		self.Bind(wx.EVT_CLOSE, self.onExit)
		# To dismiss the frame with the escape key.
		panel.Bind(wx.EVT_CHAR_HOOK, self.on_key)

		self.libraries_dir= os.path.join(getChosenDataPath(), 'linkLibrary-addonFiles')
		#log.info(f'libraries_dir: {self.libraries_dir}')
		allFiles= [os.path.splitext(f) for f in os.listdir(self.libraries_dir)]
		self.libraryNames= sorted([name for name, ext in allFiles if ext== '.json'], key= lambda s: s.lower())
		#log.info(f'libraryNames: {self.libraryNames}')
		self.sublibraryNames= [name for name, ext in allFiles if ext== '' and name in self.libraryNames]
		#log.info(f'sublibraryNames: {self.sublibraryNames}')

	def makePopupMenu(self):
		self.menu= wx.Menu()
		for library in self.libraryNames:
			item = self.menu.Append(wx.ID_ANY, library)
			self.Bind(wx.EVT_MENU, lambda evt , args= library : self.onMenuItem(evt, args), item)
			if library in self.sublibraryNames:
				# It has sub libraries.
				self.appendsubmenu(self.menu, submenuLabel= library)
		return self.menu

	def appendsubmenu(self, mainMenu, submenuLabel: str):
		sublibrary_dir= os.path.join(self.libraries_dir, submenuLabel)
		sublibraries = [
		name for f in os.listdir(sublibrary_dir)
		for name, ext in [os.path.splitext(f)]
		if ext == '.json'
		]
		#log.info(f'sublibraries: {sublibraries}')
		sublibraries= sorted(sublibraries, key= str.lower)
		menu_sub= wx.Menu()
		for sublibrary in sublibraries:
			item= menu_sub.Append(wx.ID_ANY, sublibrary)
			# Add item id to subMenuId2parent dictionary, and parent library as value.
			self.subMenuId2parent[item.GetId()]= submenuLabel
			self.Bind(wx.EVT_MENU, lambda evt , args=sublibrary: self.onMenuItem(evt, args), item)
		mainMenu.AppendSubMenu(menu_sub, submenuLabel)

	def onMenuItem(self,event, label: str):
		#label is the name of library or menu item press.
		menu_id = event.GetId()
		isSubmenu= menu_id in self.subMenuId2parent
		# if it is a sublibraries
		if isSubmenu:
			# Close any sublibrary dialog if opened.
			# if it stays opened, the json file will be overwritten, and link not added.
			if LinkSublibrary.sublibraryInstance:
				LinkSublibrary.sublibraryInstance.onCancel(None)
			# name of folder in which this sublibraries is found.
			subMenuLabel= self.subMenuId2parent.get(menu_id)
			#log.info(f'subMenu label: {subMenuLabel}')
			libraryPath= os.path.join(self.libraries_dir, subMenuLabel, label+'.json')
		else:
			# it is a major library and not sub library.
			# Close any library dialog if opened.
			# if it stays opened, the json file will be overwritten, and link not added.
			if LinkDialog.currentInstance:
				LinkDialog.currentInstance.onCancel(None)

			libraryPath= os.path.join(self.libraries_dir, label+'.json')
		#log.info(f'libraryPath: {libraryPath}')
		link, title= self.getLinkAndTitleOfWebPage()
		# Add the link, and title as label to the library
		try:
			with open(libraryPath, encoding= 'utf-8') as f:
				libraryDict= json.load(f)
			if link in libraryDict:
				if gui.messageBox(
				# Translators: Message displayed when trying to add a link already present in the library.
				_("This link is already present in {library} library, under {label} label;\n"
				" Do you still want to replace it with the one you are about to add?.").format(library= label, label= libraryDict[link]['label']),
				# Translators: Title of message box.
				_('Warning'),
				wx.YES|wx.NO|wx.ICON_QUESTION)== wx.NO:
					return

			libraryDict[link]= {"label": title, "about": ""}
			with open(libraryPath, 'w', encoding= 'utf-8') as f:
				json.dump(libraryDict, f, ensure_ascii= False, indent= 4)
		except Exception as e:
			gui.messageBox(
			# Translators: Message displayed when getting an error trying to add a link on the fly.
			_("Unable to add the link to the library"), 
			# Translators: Title of message box
			_("Error"), wx.OK|wx.ICON_ERROR)
			raise e
			return
		core.callLater(100, ui.message, 
		# Translators: Message displayed after adding the link successfuly.
		_("Information: The link was added successfuly to {library} library").format(library= label))
		self.Destroy()

	def getLinkAndTitleOfWebPage(self):
		obj= self.navigatorObjectTreeInterceptor
		link = obj.documentConstantIdentifier
		#log.info(f'link: {link}')
		#get title
		title= self.foregroundObject.name
		pattern, text = r'[-—]', title[::-1]
		# we will split either on - or —, after we have reversed the title
		lst= re.split(pattern, text, maxsplit= 1)
		if len(lst)> 1:
			title= lst[-1][::-1].strip()
		#log.info(f'title: {title}')
		return link, title

	def onChooseLibrary(self, event):
		# clear the dictionary that maps id to subMenu label
		self.subMenuId2parent= {}
		btn = event.GetEventObject()
		pos = btn.ClientToScreen( (0,0) )
		menu= self.makePopupMenu()
		self.PopupMenu(menu, pos)
		self.menu.Destroy()

	def on_key(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Destroy()
		else:
			event.Skip()

	def onExit(self,event):
		self.Destroy()
