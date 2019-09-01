# -*- coding: utf-8 -*-
# linkLibrary
# Copyright 2019 ibrahim hamadeh, released under GPLv2.0
# An addon that helps collect and arrange and access easily informations related to links under specific categories

import globalPluginHandler 
import core, ui
import wx, gui
import config
import globalVars
import os
import shutil
from .libraryDialog import LibraryDialog
import addonHandler
addonHandler.initTranslation()

# path of library files for the addon, home user lirectory/linkLibrary-addonFiles.
homeDirectory= os.path.expanduser('~')
LIBRARIES_DIR= os.path.abspath(os.path.join(homeDirectory, 'linkLibrary-addonFiles')).decode("mbcs")

#initial value when no instance of dialog is opened
LIBRARYDIALOG= None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Link Library")

	def __init__(self):
		super(GlobalPlugin, self).__init__()

		self.makeAddonMenu()

	def makeAddonMenu(self):
		self.preferencesMenu= gui.mainFrame.sysTrayIcon.preferencesMenu
		self.addonMenu= wx.Menu()
		# Translators: label of submenu.
		self.subMenu= self.preferencesMenu.AppendSubMenu(self.addonMenu, _("&Link Library"))
		#open library dialog menu
		self.openLibraryDialog= self.addonMenu.Append(wx.ID_ANY, _("Open Library Dialog"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onOpenLibraryDialog, self.openLibraryDialog)
		# Close Link Dialog After menu item
		self.closeLinkDialogAfter= self.addonMenu.Append(wx.ID_ANY, _("Close Link Dialog After..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCloseLinkDialogAfter, self.closeLinkDialogAfter)
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

	def onOpenLibraryDialog(self, evt):
		self.script_openLibraryDialog(None)

	def onCloseLinkDialogAfter(self, evt):
		gui.mainFrame._popupSettingsDialog(LinkDialogSettings)

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
			LIBRARYDIALOG= LibraryDialog(gui.mainFrame)
		else:
			LIBRARYDIALOG.Raise()

	# Translators: message displayed in input help mode for openning  choose library dialog.
	script_openLibraryDialog.__doc__ = _('Open  Link Library dialog.')

	__gestures = {
		'KB:NVDA+w':'openLibraryDialog'
	}

#default configuration of settings dialog
configspec={
	"closeDialogAfterActivatingALink": "boolean(default= False)"
}
config.conf.spec["linkLibrary"]= configspec

#make SettingsDialog class
class LinkDialogSettings(gui.SettingsDialog):
	# Translators: title of the dialog
	title= _("Link Library Settings")

	def makeSettings(self, sizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		# Translators: label of the check box 
		self.closeDialogCheckBox=wx.CheckBox(self,label=_("&Close Link Dialog after activating a link"))
		self.closeDialogCheckBox.SetValue(config.conf["linkLibrary"]["closeDialogAfterActivatingALink"])
		settingsSizerHelper.addItem(self.closeDialogCheckBox)

	def onOk(self, evt):
		config.conf["linkLibrary"]["closeDialogAfterActivatingALink"]= self.closeDialogCheckBox.IsChecked() 
		super(LinkDialogSettings, self).onOk(evt)

	def postInit(self):
		self.closeDialogCheckBox.SetFocus()

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
		self.directoryEdit.Value = os.path.join(globalVars.appArgs.configPath, "linkLibrary-addonFiles")

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
			shutil.copytree(LIBRARIES_DIR, destination)
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
		try:
			shutil.rmtree(LIBRARIES_DIR, ignore_errors= True)
			shutil.copytree(source_directory, LIBRARIES_DIR)
		except Exception as e:
			# Translators: message presented when import folder fails
			gui.messageBox(_("Import libraries folder failed."),
			_("Error"), wx.OK|wx.ICON_ERROR)
			raise e
		else:
			# Translators: message presented when importing libraries folder succeeded.
			core.callLater(100, ui.message, _("Libraries folder imported successfuly."))

	def onCancel(self, evt):
		self.Destroy()