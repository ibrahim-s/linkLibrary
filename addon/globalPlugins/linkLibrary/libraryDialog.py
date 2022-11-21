# -*- coding: utf-8 -*-
# libraryDialog.py
# Copyright 2019 ibrahim hamadeh, released under GPLv2.0
# See the file COPYING for more details.
# graphical user interface for libraries dialog

import wx, gui, core, os, sys, ui
import api, shutil, codecs, config, globalVars
import json
import re
from logHandler import log
from .links import Link
from .linkDialog import LinkDialog

import addonHandler
addonHandler.initTranslation()

CURRENT_DIR= os.path.dirname(os.path.abspath(__file__))

def addLibrary(message, caption, oldName=None):
	''' Entering the name of new library, or renaming existing one by passing a value to oldName in this function.'''
	if oldName:
		name=wx.GetTextFromUser(message, caption, oldName).strip()
	else:
		name= wx.GetTextFromUser(message, caption).strip()
	if name in LibraryDialog.libraryFiles:
		gui.messageBox(
		# Translators: message displayed when the name is present for another library.
		_('This name is already present for another library, enter another name please'), 
		# Translators: Title of messagebox.
		_('Warning'))
		return addLibrary(message, caption, oldName)
	return name

def makeHtmlFile(libraryName, libraryData, newpath):
	''' Make Html file out of json library file.
	'''
	with codecs.open(newpath, 'wb', encoding= 'utf-8') as html:
		html.write(u"""<!DOCTYPE html><html lang="en"><head>
			<meta charset="UTF-8">
<title>Bookmarks </title>
		</head><body>
		<h1>Link Library Bookmarks</h1>
		<DT><H3>{}</H3>
		<DL><p>""".format(libraryName)
		)
		for url, label, about in libraryData:
			html.write(u'<DT><a href= "{}">{}</a></DT>'.format('http://'+url if url.startswith('www.') else url, label))
			html.write(u'{}'.format(about))
		html.write(u'</DL></body></html>')
		return True

def validateLibraryFile(filePath):
	''' checking if the library file to be imported is valid. if it is not it returns False'''
	try:
		with open(filePath, encoding= 'utf-8') as f:
			d= json.load(f)
	except Exception as e:
		return False
	else:
		#log.info(d)
		#the file has opened but we want to verify it's content
		#if empty dictionary, that is empty json file we accept it.
		if d== {}:
			return True
		if d and isinstance(d, dict):
			try:
				[(key, d[key]['label'], d[key]['about']) for key in d]
			except Exception as e:
				log.info('Error in verifying json file', exc_info=True)
				return False
			else:
				return True
		return False

 #Popup menu class
class LibraryPopupMenu(wx.Menu):
	''' The menu that pops up upon right clicking on the list box.'''
	def __init__(self, parent, libraries_directory, objectId):
		super(LibraryPopupMenu, self).__init__()
        
		self.parent = parent
		self.LIBRARIES_DIR= libraries_directory
		self.objectId= objectId

#add a subMenu for exporting a library
		subMenu= wx.Menu()
		self.exportJson = subMenu.Append(wx.ID_ANY, 
		# Translators: label of menu to export library as json file
		_('Json File'))
		self.exportHtml = subMenu.Append(wx.ID_ANY, 
		# Translators: label of menu to export library as html.
		_('Html File'))
		self.AppendSubMenu(subMenu, 
		# Translators: label obj subMenu items for exporting a library.
		_('Export Library As'))
		self.Bind(wx.EVT_MENU, self.onExportJson, self.exportJson)
		self.Bind(wx.EVT_MENU, self.onExportHtml, self.exportHtml)

		#Add Import Library menu
		importLibrary= wx.MenuItem(self, wx.ID_ANY, 
		# Translators: label obj menu items to import a library.
		_('Import Library(as Json)'))
		self.Append(importLibrary)
		self.Bind(wx.EVT_MENU, self.onImport, importLibrary)

	def onExportJson(self, evt):
		dlg = wx.DirDialog(self.parent, "Choose a directory:",
		style=wx.DD_DEFAULT_STYLE
| wx.DD_DIR_MUST_EXIST
		)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		path_chosen= dlg.GetPath()
		#log.info(path_chosen)

		if path_chosen:
			library_name= self.parent.FindWindowById(self.objectId).GetStringSelection()
			try:
				shutil.copy(os.path.join(self.LIBRARIES_DIR, library_name+'.json'), path_chosen)
			except Exception as e:
				wx.CallAfter(gui.messageBox,
				# Translators: message of error dialog displayed when cannot export library file.
				_("Failed to export library"),
				# Translators: title of error dialog .
				_("Error"),
				wx.OK|wx.ICON_ERROR)
				raise e
			else:
				core.callLater(10, ui.message,
				# Translators: Message presented when library has been exported.
				_("Information: Library Exported"))
		dlg.Destroy()

	def onExportHtml(self, evt):
		library_name= self.parent.FindWindowById(self.objectId).GetStringSelection()
		path= os.path.join(self.LIBRARIES_DIR, library_name+'.json')
		try:
			with open(path, 'r') as f:
				d= json.load(f)
		except Exception as e:
			gui.messageBox(
			_('Failed to open library, or may be library file is not valid.'),
			_('Error'), wx.OK|wx.ICON_ERROR)
			log.info('Failed to open library', exc_info= True)
			return
		else:
			# Opening the library file succeeded
			#the library data as list of tuple of three items url, label, about sorted by the second that is the label of the link.
			library_data= sorted([(url, d[url]['label'], d[url]['about']) for url in d], key= lambda x: x[1])

		dlg = wx.DirDialog(self.parent, "Choose a directory:",
		style=wx.DD_DEFAULT_STYLE
| wx.DD_DIR_MUST_EXIST
		)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		path_chosen= dlg.GetPath()
		#log.info(path_chosen)
		if path_chosen:
			html_path= os.path.join(path_chosen, library_name+ '.html')
			try:
				makeHtmlFile(library_name, library_data, html_path)
			except Exception as e:
				wx.CallAfter(gui.messageBox,
				# Translators: message of error dialog displayed when cannot export library file.
				_("Failed to export library"),
				# Translators: title of error dialog .
				_("Error"),
				wx.OK|wx.ICON_ERROR)
				raise e
			else:
				core.callLater(200, ui.message,
				# Translators: Message presented when library has been exported.
				_("Information: Library Exported"))
		dlg.Destroy()

	def onImport(self, evt):
		''' Importing a new json library file to the link library file directory'''
		dlg= wx.FileDialog(self.parent, "Choose File", "", "", 
		"Json Files (*.json)|*.json", 
		wx.FD_FILE_MUST_EXIST)

		if dlg.ShowModal()!= wx.ID_OK:
			dlg.Destroy()
			return
		file_path= dlg.GetPath()
		dlg.Destroy()
		#log.info(file_path)
		if file_path:
			if not validateLibraryFile(file_path):
			#validation of the json file did not succeed
			# Translators: Message to be displayed when import fails due to validation problem
				gui.messageBox(_('Importfailed; chosen file seems not valid.'),
				# Translators: Title of message box
				_('Import Error'), wx.OK|wx.ICON_ERROR)
				return
			file_name= os.path.split(file_path)[1]
			if file_name in os.listdir(self.LIBRARIES_DIR):
				file_name= self.importingLibraryWithNamePresent(file_name, file_path)
			library_name= os.path.splitext(file_name)[0]
			try:
				shutil.move(file_path, os.path.join(self.LIBRARIES_DIR, file_name))
			except Exception as e:
			# Translators: Message displayed when importing failed after validation succeeded
				gui.messageBox(_('Sorry, importing of library failed'),
				# Translators: Title of message box
				_('Error', wx.OK|wx.ICON_ERROR))
				raise e
			else:
				if library_name not in LibraryDialog.libraryFiles:
					# this checking is important in case obj merging 2 libraries, if we do not do it we will have 2 files with same name in libraries list.
					LibraryDialog.libraryFiles.append(library_name)
				LibraryDialog.libraryFiles.sort()
				self.parent.refreshLibraries(str= library_name)
				core.callLater(200, ui.message,
				# Translators: Message presented when library has been imported.
				_("Information: Library imported."))

	def importingLibraryWithNamePresent(self, filename, filepath):
		'''Importing a library, that has a name already present in existing libraries'''
		library_name= os.path.splitext(filename)[0]
		# Translators: Ask the user if he wants to merge the two libraries or not.
		if gui.messageBox(_("A library with similar name already exists, do you want to merge the two libraries?"),
			# Translators: Title of message box
			_("Information"),
			style= wx.YES_NO|wx.ICON_QUESTION)== wx.NO:
			libraryNames= [os.path.splitext(f)[0] for f in os.listdir(self.LIBRARIES_DIR) if f.startswith(library_name)]
			if len(libraryNames)== 1:
				return library_name + ' (2).json'
			nums= []
			# library names that end with a number between paranthesis
			libraryNames= [name for name in libraryNames if re.match(r'.+\([0-9]+\)', name)]
			try:
				for name in libraryNames:
					# n is the number to be between paranthesis
					n=name[name.rfind('(')+1: -1]
					nums.append(int(n))
				raisedNum= max(nums)+ 1
			except:
				raisedNum=2
			return library_name+ " (%s).json"% raisedNum
		else:
			# Now if the user wants to merge the two libraries.
			#log.info('mergeing two libraries ...')
			with open(filepath, encoding= 'utf-8') as f:
				importedDict= json.load(f)
			with open(os.path.join(self.LIBRARIES_DIR, filename), encoding= 'utf-8') as f:
				existedDict= json.load(f)
			importedDict.update(existedDict)
			mergedDict= importedDict
			with open(filepath, 'w', encoding= 'utf-8') as f:
				json.dump(mergedDict, f, ensure_ascii= False, indent= 4)
			return filename

class LibraryDialog(wx.Dialog):
	def __init__(self, parent, path):
		pathLabel= config.conf["linkLibrary"]["chosenDataPath"]
		# pathLabel is the label chosen by the user, for the directory that stores the data files
		# Translators: Title of dialog with the path label as suffix.
		title= _("Link Library - {}").format(pathLabel)
		super(LibraryDialog, self).__init__(parent, title= title)
		self.LIBRARIES_DIR= os.path.join(path, 'linkLibrary-addonFiles')
		self.createDirectoryIfNotExist()

		panel= wx.Panel(self)
		mainSizer=wx.BoxSizer(wx.HORIZONTAL)
		listBoxSizer= wx.BoxSizer(wx.VERTICAL)
		# Translators: label of libraries list box.
		staticText= wx.StaticText(panel, -1, _('Choose a library'))
		self.listBox = wx.ListBox(panel,-1, style= wx.LB_SINGLE)
		#self.listBox.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.listBox.Bind(wx.EVT_CONTEXT_MENU, self.OnRightDown)
		# wx.EVT_CONTEXT_MENU is used in NVDA 2021.1, for wx.EVT_RIGHT_DOWN seized to work.
		self.listBox.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
		listBoxSizer.Add(staticText, 0, wx.ALL, 5)
		listBoxSizer.Add(self.listBox, 1, wx.ALL|wx.EXPAND, 5)
		mainSizer.Add(listBoxSizer, 1, wx.ALL, 5)

		buttonSizer= wx.BoxSizer(wx.VERTICAL)
		# Add library button
		self.add= wx.Button(panel, wx.ID_ANY,
		# Translators: Label of Add button
		_("Add"))
		self.add.Bind(wx.EVT_BUTTON, self.onAdd)
		buttonSizer.Add(self.add, 1,wx.ALL, 10)
		# Rename button
		self.rename= wx.Button(panel, wx.ID_ANY,
		# Translators: Label of Rename button
		_("Rename"))
		self.rename.Bind(wx.EVT_BUTTON, self.onRename)
		buttonSizer.Add(self.rename, 1,wx.ALL, 10)
		# Remove button
		self.remove= wx.Button(panel, wx.ID_ANY,
		# Translators: Label of Remove button
		_("Remove"))
		self.remove.Bind(wx.EVT_BUTTON, self.onRemove)
		buttonSizer.Add(self.remove, 1,wx.ALL, 10)
		self.ok= wx.Button(panel, wx.ID_OK,
		# Translators: Label of OK button
		_('OK'))
		self.ok.SetDefault()
		self.ok.Bind(wx.EVT_BUTTON, self.onOk)
		buttonSizer.Add(self.ok, 1,wx.ALL, 10)
		self.cancel= wx.Button(panel, wx.ID_CANCEL,
		# Translators: Label of Cancel button
		_("Cancel"))
		self.cancel.Bind(wx.EVT_BUTTON, self.onCancel)
		buttonSizer.Add(self.cancel, 0, wx.EXPAND|wx.ALL, 10)
		mainSizer.Add(buttonSizer, 0, wx.EXPAND|wx.ALL, 5)
		panel.SetSizer(mainSizer)
		self.postInit()

	def createDirectoryIfNotExist(self):
		path= self.LIBRARIES_DIR
		#path is the full path, with the base folder of the directory.
		if os.path.isdir(path):
			return
		try:
			os.mkdir(path)
			#create one file in the directory named general.json
			with open(os.path.join(path, "general.json"), 'w') as f:
				f.write("{}")
		except:
			log.info("Failed to create directory", exc_info=1)
			core.callLater(100, ui.message,
			# Translators: Message displayed when failing to create new directory for data files
			_("Information:Failed to create directory."))
			return

	def postInit(self):
		#log.info('under postInit of libraries file dialog...')
		foundFiles= [os.path.splitext(f) for f in os.listdir(self.LIBRARIES_DIR)]
		# foundFiles is a list of tuples, first element of the tuple is the name of file and the second is it's extension
		libraryFiles= sorted([name for name, ext in foundFiles if ext== '.json'], key= lambda s: s.lower())
		# We picked only .json files, even if there are other files in the folder.
		LibraryDialog.libraryFiles= libraryFiles
		self.listBox.Set(libraryFiles)
		#log.info(f'list count:{self.listBox.GetCount()}')
		if self.listBox.GetCount()> 0:
			self.listBox.SetSelection(0)
		self.Raise()
		self.Show()

	def OnRightDown(self, e):
		#log.info('under right down handler') 
		obj= e.GetEventObject()
		id= obj.GetId()
		menu= LibraryPopupMenu(self, self.LIBRARIES_DIR, id)
		self.PopupMenu(menu, e.GetPosition())
		menu.Destroy()
		#log.info('destroying pop up menu')

	def onAdd(self, evt):
		# Translators: Message displayed when adding a new library.
		message= _('Enter library name please')
		# Translators: Title of dialog.
		caption= _('Add Library')
		name=addLibrary(message, caption)
		#log.info(name)
		if not name:
			return
		filename= api.filterFileName(name)+'.json'
		filepath= os.path.join(self.LIBRARIES_DIR, filename)
		#log.info('filepath to add: %s'%filepath)
		try:
			with open(filepath, 'w') as f:
				f.write("{}")
		except Exception as e:
			raise e
		LibraryDialog.libraryFiles.append(name)
		LibraryDialog.libraryFiles.sort(key= str.lower)
		self.refreshLibraries(str= name)
		# name is the item to be selected after refresh

	def onRename(self, evt):
		# Translators: Message displayed when renaming a library
		message= _('Enter new name please')
		# Translators: Title of dialog to enter new name.
		caption= _('rename')
		oldName= self.listBox.GetStringSelection()
		i= LibraryDialog.libraryFiles.index(oldName)
		LibraryDialog.libraryFiles.remove(oldName)
		newname= addLibrary(message, caption, oldName)
		#log.info('newname: %s'%newname)
		if not newname or newname== oldName:
			LibraryDialog.libraryFiles.insert(i, oldName)
			return
		else:
			newname= api.filterFileName(newname)
			os.rename(os.path.join(self.LIBRARIES_DIR, oldName+'.json'), os.path.join(self.LIBRARIES_DIR, newname+'.json'))
			#log.info(LibraryDialog.libraryFiles)
			LibraryDialog.libraryFiles.append(newname)
			LibraryDialog.libraryFiles.sort(key= str.lower)
			self.refreshLibraries(str= newname)

	def onRemove(self, evt):
		toRemove= self.listBox.GetStringSelection()
		i= self.listBox.GetSelection()
		# number of items or libraries in the list.
		numItems= self.listBox.GetCount()
		if gui.messageBox(
		# Translators: Message displayed upon removing a library.
		_('Are you sure you want to remove {} library, this can not be undone?').format(toRemove),
		# Translators: Title of dialog.
		_('Warning'), wx.ICON_QUESTION | wx.YES_NO)== wx.NO:
			return
		os.remove(os.path.join(self.LIBRARIES_DIR, toRemove+'.json'))
		LibraryDialog.libraryFiles.remove(toRemove)
		sel= i if i!= numItems-1 else i-1
		#log.info(f'sel after onRemove: {sel}')
		self.refreshLibraries(i= sel)
		# i is the index of item to be selected after refresh

	def refreshLibraries(self, str=None, i= None):
		'''
		@str: name of selected library
		@i: index of selected library
		'''
		self.Hide()
		self.listBox.Set(LibraryDialog.libraryFiles)
		if str:
			self.listBox.SetStringSelection(str)
		if i  is not None and i> -1:
			self.listBox.SetSelection(i)
		self.listBox.SetFocus()
		self.Show()

	def onKillFocus(self, evt):
		library_num= self.listBox.GetCount()
		state= bool(library_num)
		self.rename.Enabled= state
		self.remove.Enabled= state
		evt.Skip()

	def onOk(self, evt):
		#log.info('under ok button')
		i= self.listBox.GetSelection()
		if i != -1:
			filename= self.libraryFiles[i]
			if  LinkDialog.currentInstance:
				gui.messageBox(
				# Translators: Message be displayed when a library dialog is already opened.
			_('A library dialog is already opened; Close it first please.'),
			# Translators: Title of dialog.
			_('information'))
				return
			else:
				wx.CallAfter(self.openLinkDialog, filename, self.LIBRARIES_DIR)
			# We have commented the below line, so that main window will stay open when opening a library, and when closing it focus return to main window.
			#self.Destroy()

	def openLinkDialog(self, filename, librariesPath):
		dialog= LinkDialog(self, filename, librariesPath)
		LinkDialog.currentInstance= dialog
		LinkDialog.libraryFiles= LibraryDialog.libraryFiles[:]

	def onCancel(self, evt):
		self.Destroy()
