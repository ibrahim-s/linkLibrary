# -*- coding: utf-8 -*-
#linkLibrary
#Copyright 2019 ibrahim hamadeh, released under GPLv2.0
#See the file COPYING for more details.
# An addon that helps collect and arrange and access easily informations related to links under specific categories

import globalPluginHandler 
import core, ui
import wx, gui
import os, sys
import config
import globalVars
import shutil
from configobj import ConfigObj
from logHandler import log
from .libraryDialog import LibraryDialog
import addonHandler
addonHandler.initTranslation()

# default path of library files for the addon, home user lirectory
homeDirectory= os.path.expanduser('~')

#default configuration 
configspec={
	"chosenDataPath": "string(default='Home user directory')",
	"closeDialogAfterActivatingALink": "boolean(default= False)"
}
config.conf.spec["linkLibrary"]= configspec

#path of ini file to store available paths
#iniFile= os.path.join(globalVars.appArgs.configPath, "linkLibrary.ini")
iniFile= os.path.join(globalVars.appArgs.configPath, "addons", "linkLibrary", "availablePaths", "paths.ini")
iniFile= iniFile if sys.version_info.major==3 else iniFile.decode('mbcs')

#creating ini file for available directories or paths
def createIniFileForAvailablePaths(iniFile):
	#Create parent directory of iniFile if not present
	availablePaths= os.path.join(globalVars.appArgs.configPath, "addons", "linkLibrary", "availablePaths")
	if not os.path.exists(availablePaths): os.mkdir(availablePaths)
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
	#directory or value for this pathName, as saved in paths.inie
	try:
		chosenPath= os.path.abspath(pathsHandle["availablePaths"][pathName])
	except KeyError:
#		chosenPath= os.path.abspath(pathsHandle["availablePaths"]["Home user directory"])
		chosenPath= homeDirectory
		# Key not exist in availablePaths, so better remove it from base configuration, and return the value of chosenDataPath to Home user directory
		config.conf["linkLibrary"]["chosenDataPath"]= 'Home user directory'
		# Better save the configuration
		config.conf.save()
		log.info("Error in getting chosenDataPath from availablePaths", exc_info=1)
	finally:
		chosenPath= chosenPath if sys.version_info.major== 3 else chosenPath.decode('mbcs')
		return chosenPath
#log.info(getChosenDataPath())
#initial value when no instance of dialog is opened
LIBRARYDIALOG= None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Link Library")

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		#if not os.path.exists(iniFile):
			#createIniFileForAvailablePaths(iniFile)

		self.makeAddonMenu()

	def makeAddonMenu(self):
		self.preferencesMenu= gui.mainFrame.sysTrayIcon.preferencesMenu
		self.addonMenu= wx.Menu()
		# Translators: label of submenu.
		self.subMenu= self.preferencesMenu.AppendSubMenu(self.addonMenu, _("&Link Library"))
		# Link library settings menu item.
		self.linkLibrarySetting= self.addonMenu.Append(wx.ID_ANY, _("Link Library Setting"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onLinkLibrarySetting, self.linkLibrarySetting)
		#open library dialog menu item
		self.openLibraryDialog= self.addonMenu.Append(wx.ID_ANY, _("Open Library Dialog"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onOpenLibraryDialog, self.openLibraryDialog)
		# Copy Library Folder menu item.
		self.copyLibraryFolder= self.addonMenu.Append(wx.ID_ANY, _("Copy Library Folder"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCopyLibrariesFolder, self.copyLibraryFolder)
		#Import Library Folder menu item.
		self.importLibraryFolder= self.addonMenu.Append(wx.ID_ANY, _("Import Library Folder"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onImportLibrariesFolder, self.importLibraryFolder)

	def terminate(self):
		try:
			self.preferencesMenu.Remove(self.subMenu)
		except:
			pass

	def onLinkLibrarySetting(self, evt):
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

	def script_openLibraryDialog(self, gesture):
		global LIBRARYDIALOG
		if not LIBRARYDIALOG:
			LIBRARYDIALOG= LibraryDialog(gui.mainFrame, getChosenDataPath())
		else:
			LIBRARYDIALOG.Raise()

	# Translators: message displayed in input help mode for openning  choose library dialog.
	script_openLibraryDialog.__doc__ = _('Open  Link Library dialog.')
#make SettingsDialog class

class LinkDialogSettings(gui.SettingsDialog):
	# Translators: title of the dialog
	title= _("Link Library Settings")
	pathInfoDict= {}
	#configHandle= ConfigObj(iniFile, encoding= 'utf-8')

	def makeSettings(self, sizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		# Translators: label of cumbo box of available paths to contain data files.
		self.availablePaths= settingsSizerHelper.addLabeledControl(_("Choose Path to store Data Files"), wx.Choice, choices=[key for key in pathsHandle["availablePaths"]])
		#log.info([key for key in self.configHandle["availablePaths"]])
		self.availablePaths.Bind(wx.EVT_CHOICE, self.onAvailablePaths)
		# Translators: label of button to add a new path.
		self.addPathBtn= settingsSizerHelper.addItem( wx.Button(self, -1, label= _("Add New Path")))
		self.addPathBtn.Bind(wx.EVT_BUTTON, self.onAddPath)
		# Translators: label of Remove path button.
		self.removePathBtn= settingsSizerHelper.addItem( wx.Button(self, -1, label= _("Remove Selected Path")))
		self.removePathBtn.Bind(wx.EVT_BUTTON, self.onRemovePath)
		# Translators: label of the check box 
		self.closeDialogCheckBox=settingsSizerHelper.addItem(wx.CheckBox(self,label=_("&Close dialog after activating a link")))
		self.closeDialogCheckBox.SetValue(config.conf["linkLibrary"]["closeDialogAfterActivatingALink"])
		#self.closeDialogCheckBox.SetValue(self.configHandle.as_bool("closeDialogAfterActivatingALink"))

	def postInit(self):
		self.availablePaths.SetStringSelection(config.conf["linkLibrary"]["chosenDataPath"])
#		self.availablePaths.SetStringSelection(self.configHandle["chosenDataPath"])
		#log.info(self.availablePaths.GetStringSelection())
		if self.availablePaths.GetStringSelection()== "Home user directory":
			#log.info('under if')
			self.removePathBtn.Enabled= False
		self.availablePaths.SetFocus()

	def onAvailablePaths(self, evt):
		state= self.availablePaths.StringSelection != 'Home user directory'
		self.removePathBtn.Enabled= state

	def onAddPath(self, evt):
		#gui.mainFrame._popupSettingsDialog(AddPathDialog, self.pathInfo)
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
			# Translators: The title of the confirmation dialog for deletion of a configuration profile.
			_("Warning"),
			wx.OK | wx.CANCEL | wx.ICON_QUESTION
			) != wx.OK:
				return
			if name== config.conf["linkLibrary"]["chosenDataPath"]:
				#return to default path
				config.conf["linkLibrary"]["chosenDataPath"]= homeDirectory
			if name in pathsHandle["availablePaths"]:
				del pathsHandle["availablePaths"][name]
			if name in self.pathInfoDict:
				del self.pathInfoDict[name]
			self.availablePaths.Delete(i)
			self.postInit()

	def onOk(self, evt):
		pathName= self.availablePaths.GetStringSelection()
		log.info(self.pathInfoDict)
		for key, value in self.pathInfoDict.items():
			#config.conf["linkLibrary"]["availablePaths"][key]= value
			#store the addedpaths in the ini file
			pathsHandle["availablePaths"][key]= value
#		self.configHandle.write()
		pathsHandle.write()
		config.conf["linkLibrary"]["chosenDataPath"]= pathName
		config.conf["linkLibrary"]["closeDialogAfterActivatingALink"]= self.closeDialogCheckBox.IsChecked() 
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
		super(CopyDialog, self).__init__(parent, title= "Copy Libraries Folder")

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
		#self.directoryEdit.Value = os.path.join(globalVars.appArgs.configPath, "linkLibrary-addonFiles")

		bHelper = sHelper.addDialogDismissButtons(gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
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
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		if not os.path.exists(selected_path) or not os.path.isdir(selected_path):
			# Translators: The message displayed when the user specifies an invalid destination directory
			gui.messageBox(_("%s is invalid, please select a valid directory path.")%selected_path,
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
		if not os.path.exists(selected_path) or not os.path.isdir(selected_path):
			# Translators: message displayed when path selected is not valid
			gui.messageBox(_("Sorry, but %s is invalid path.")%selected_path,
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		self.Hide()
		self.importFolder(selected_path)
		self.Destroy()

	def importFolder(self, source_directory):
		if not os.path.basename(source_directory)== "linkLibrary-addonFiles" or not any(os.path.splitext(_file)[-1]== '.pickle' for _file in os.listdir(source_directory)):
			# Translators: message displayed when folder to be imported not named linkLibrary-addonFiles, or all files in it has not .pickle extension
			gui.messageBox(_("Check that the folder name is linkLibrary-addonFiles, and all files in it has a .pickle extension."),
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
	#pathInfo parameter is to pass the infos about the new path name and value to the LinkDialogSettings dialog.
	def __init__(self,parent):
		# Translators: Title of dialog.
		title=_("Add new path")
		super(AddPathDialog, self).__init__(parent, title= title)
		self.parent= parent

		mainSizer= wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
				# Translators: The label of a grouping containing controls to select the destination directory in the Import dialog.
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
		log.info(pathValue)
		if not pathValue:
			gui.messageBox(
			# Translators: The message displayed when the user has not specified a directory
			_("Please specify a directory."),
			_("Warning"), wx.OK|wx.ICON_WARNING)
			return
		if not os.path.exists(pathValue) or not os.path.isdir(pathValue):
			# Translators: message displayed when path selected is not valid
			gui.messageBox(_("Sorry, but %s is invalid path.")%pathValue,
			_("Error"), wx.OK|wx.ICON_ERROR)
			return
		pathName= self.nameEntry.Value or pathValue
		pathName= pathName.strip()
		parent= self.parent
		parent.pathInfoDict[pathName]= pathValue
		parent.availablePaths.Append(pathName)
		parent.availablePaths.SetStringSelection(pathName)
		parent.onAvailablePaths(None)
		#log.info(pathName)
		self.Destroy()

	def onCancelButton(self, evt):
		self.Destroy()