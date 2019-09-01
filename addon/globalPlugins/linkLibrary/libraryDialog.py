# -*- coding: utf-8 -*-
#libraryDialog.py
# Copyright 2019 ibrahim hamadeh, released under GPLv2.0
#graphical user interface for libraries dialog

import wx, gui, core, os, ui
import shutil
import codecs
#for compatibility with python3
try:
	import cPickle as pickle
except ImportError:
	import pickle

from logHandler import log
from .links import Link
from .linkDialog import LinkDialog

import addonHandler
addonHandler.initTranslation()

CURRENT_DIR= os.path.dirname(os.path.abspath(__file__))
# path of library files for the addon
# os.path.expanduser('~') is the home user directory
LIBRARIES_DIR= os.path.join(os.path.expanduser('~'), 'linkLibrary-addonFiles').decode("mbcs")

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
	''' Make Html file out of pickle library file.'''
	with codecs.open(newpath, 'wb', encoding= 'utf-8') as html:
		html.write(u"""<!DOCTYPE html><html lang="en"><head>
			<meta charset="UTF-8">
<title>Bookmarks </title>
		</head><body>
		<h1>Link Library Bookmarks</h1>
		<DT><H3>{}</H3>
		<DL>""".format(libraryName)
		)
		for url, label, about in libraryData:
			html.write(u'<DT><a href= "{}">{}</a></DT>'.format('http://'+url if url.startswith('www.') else url, label))
			html.write(u'<DD>{}</DD>'.format(about))
		html.write(u'</DL></body></html>')
		return True

def validateLibraryFile(filePath):
	''' checking if the library file to be imported is valid. if it is not it returns False'''
	try:
		with open(filePath, 'rb') as f:
#		try:
			d= pickle.load(f)
	except Exception as e:
		#gui.messageBox()
		#raise e
		return False
	else:
		log.info(d)
		#the file has opened but we want to verify it's content
		if d and isinstance(d, dict):
			try:
				[(key, d[key]['label'], d[key]['about']) for key in d]
			except Exception as e:
				#raise e
				return False
			else:
				return True
		return False

 #Popup menu class
class LibraryPopupMenu(wx.Menu):
	''' The menu that pops up upon right clicking on the list box.'''
	def __init__(self, parent, objectId):
		super(LibraryPopupMenu, self).__init__()
        
		self.parent = parent
		self.objectId= objectId

#add a subMenu for exporting a library
		subMenu= wx.Menu()
		self.exportPickle = subMenu.Append(wx.ID_ANY, 
		# Translators: label of menu to export library as pickle file
		_('Pickle File'))
		self.exportHtml = subMenu.Append(wx.ID_ANY, 
		# Translators: label of menu to export library as html.
		_('Html File'))
		self.AppendSubMenu(subMenu, 
		# Translators: label obj subMenu items for exporting a library.
		_('Export Library As'))
		self.Bind(wx.EVT_MENU, self.onExportPickle, self.exportPickle)
		self.Bind(wx.EVT_MENU, self.onExportHtml, self.exportHtml)

		#Add Import Library menu.
		importLibrary= wx.MenuItem(self, wx.ID_ANY, 
		# Translators: label obj menu items to import a library.
		_('Import Library(as pickle)'))
		self.Append(importLibrary)
		self.Bind(wx.EVT_MENU, self.onImport, importLibrary)

	def onExportPickle(self, evt):
		#if self.parent.GetObjectById(objectId).GetSelection()== -1:
			#return
		dlg = wx.DirDialog(self.parent, "Choose a directory:",
		style=wx.DD_DEFAULT_STYLE
| wx.DD_DIR_MUST_EXIST
#| wx.DD_CHANGE_DIR
		)
		if dlg.ShowModal() == wx.ID_OK:
			path_chosen= dlg.GetPath()
			log.info(path_chosen)
		#dlg.Destroy()

		if path_chosen:
			library_name= self.parent.FindWindowById(self.objectId).GetStringSelection()
			try:
				#shutil.copy(os.path.join(LIBRARIES_DIR, library_name+'.pickle'), os.path.join(path_chosen, library_name+'.pickle'))
				shutil.copy(os.path.join(LIBRARIES_DIR, library_name+'.pickle'), path_chosen)
			except Exception as e:
				wx.CallAfter(gui.messageBox,
				# Translators: message of error dialog displayed when cannot export library file.
				_("Failed to export library"),
				# Translators: title of error dialog .
				_("Error"),
				wx.OK|wx.ICON_ERROR)
				raise e
				#ui.message("Failed to export library")
			else:
				#ui.message("Library Exported.")
				core.callLater(10, ui.message,
				# Translators: Message presented when library has been exported.
				_("Information: Library Exported"))
		dlg.Destroy()
			#dlg.Destroy()

	def onExportHtml(self, evt):
		library_name= self.parent.FindWindowById(self.objectId).GetStringSelection()
		path= os.path.join(LIBRARIES_DIR, library_name+'.pickle')
		try:
			with open(path, 'rb') as f:
				d= pickle.load(f)
		## if the library file is empty return False
		#if not d: return False
		except EOFError:
			gui.messageBox(
			_('Failed to open library, or may be library selected is empty.'),
			_('Error'), wx.OK|wx.ICON_ERROR)
			return
		else:
			#the library data as list of tuple of three items url, label, about sorted by the second that is the label of the link.
			library_data= sorted([(url, d[url]['label'], d[url]['about']) for url in d], key= lambda x: x[1])

		dlg = wx.DirDialog(self.parent, "Choose a directory:",
		style=wx.DD_DEFAULT_STYLE
| wx.DD_DIR_MUST_EXIST
		)
		if dlg.ShowModal() == wx.ID_OK:
			path_chosen= dlg.GetPath()
			log.info(path_chosen)

		if path_chosen:
			#library_name= self.parent.FindWindowById(self.objectId).GetStringSelection()
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
		''' Importing a new pickle library file to the link library file directory'''
		dlg= wx.FileDialog(self.parent, "Choose File", "", "", 
		"Pickle Files (*.pickle)|*.pickle", 
		wx.FD_FILE_MUST_EXIST)

		if dlg.ShowModal()== wx.ID_OK:
			file_path= dlg.GetPath()
			log.info(file_path)
		dlg.Destroy()
		if file_path:
			if not validateLibraryFile(file_path):
			#validation of the pickle file did not succeed
			# Translators: Message to be displayed when import fails due to validation problem
				gui.messageBox(_('Importfailed; chosen file is empty or not valid.'),
				# Translators: Title of message box
				_('Import Error'), wx.OK|wx.ICON_ERROR)
				return
			file_name= os.path.split(file_path)[1]
			library_name= os.path.splitext(file_name)[0]
			try:
				shutil.move(file_path, os.path.join(LIBRARIES_DIR, file_name))
			except Exception as e:
			# Translators: Message displayed when importing failed after validation succeeded
				gui.messageBox(_('Sorry, importing of library failed'),
				# Translators: Title of message box
				_('Error', wx.OK|wx.ICON_ERROR))
				raise e
			else:
				#selected_library= self.parent.FindWindowById(self.objectId).GetStringSelection()
				LibraryDialog.libraryFiles.append(library_name)
				LibraryDialog.libraryFiles.sort()
				self.parent.refreshLibraries(str= library_name)
				core.callLater(200, ui.message,
				# Translators: Message presented when library has been imported.
				_("Information: Library imported."))

class LibraryDialog(wx.Dialog):
	def __init__(self, parent):
		super(LibraryDialog, self).__init__(parent, title= _('Link Library'))

		panel= wx.Panel(self)
		mainSizer=wx.BoxSizer(wx.HORIZONTAL)
		listBoxSizer= wx.BoxSizer(wx.VERTICAL)
		# Translators: label of libraries list box.
		staticText= wx.StaticText(panel, -1, _('Choose a library'))
		self.listBox = wx.ListBox(panel,-1, style= wx.LB_SINGLE)
		self.listBox.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.listBox.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
		listBoxSizer.Add(staticText, 0, wx.ALL, 5)
		listBoxSizer.Add(self.listBox, 1, wx.ALL|wx.EXPAND, 5)
		mainSizer.Add(listBoxSizer, 1, wx.ALL, 5)

		buttonSizer= wx.BoxSizer(wx.VERTICAL)
		# Add library button
		self.add= wx.Button(panel, wx.ID_ANY, _('Add'))
		self.add.Bind(wx.EVT_BUTTON, self.onAdd)
		buttonSizer.Add(self.add, 1,wx.ALL, 10)
		# Rename button
		self.rename= wx.Button(panel, wx.ID_ANY, _('Rename'))
		self.rename.Bind(wx.EVT_BUTTON, self.onRename)
		buttonSizer.Add(self.rename, 1,wx.ALL, 10)
		# Remove button
		self.remove= wx.Button(panel, wx.ID_ANY, _('Remove'))
		self.remove.Bind(wx.EVT_BUTTON, self.onRemove)
		buttonSizer.Add(self.remove, 1,wx.ALL, 10)
		self.ok= wx.Button(panel, wx.ID_OK, _('OK'))
		self.ok.SetDefault()
		self.ok.Bind(wx.EVT_BUTTON, self.onOk)
		#self.Bind(wx.EVT_BUTTON, self.onOk, self.ok)
		#self.ok.Hide()
		buttonSizer.Add(self.ok, 1,wx.ALL, 10)
		self.close= wx.Button(panel, wx.ID_CANCEL, _('Cancel'))
		self.close.Bind(wx.EVT_BUTTON, self.onClose)
		buttonSizer.Add(self.close, 0, wx.EXPAND|wx.ALL, 10)
		mainSizer.Add(buttonSizer, 0, wx.EXPAND|wx.ALL, 5)
		panel.SetSizer(mainSizer)
		self.postInit()

	def postInit(self):
		foundFiles= os.listdir(os.path.join(os.path.expanduser('~'), 'linkLibrary-addonFiles'))
		libraryFiles= sorted([os.path.splitext(f)[0].decode("mbcs") for f in foundFiles])
		LibraryDialog.libraryFiles= libraryFiles
		self.listBox.Set(libraryFiles)
		self.listBox.SetSelection(0)
		self.Raise()
		self.Show()

	def OnRightDown(self, e):
		log.info('under right down handler') 
		obj= e.GetEventObject()
		id= obj.GetId()
		self.PopupMenu(LibraryPopupMenu(self, id), e.GetPosition())

	def onAdd(self, evt):
		# Translators: Message displayed when adding a new library.
		message= _('Enter library name please')
		# Translators: Title of dialog.
		caption= _('Add Library')
		name=addLibrary(message, caption)
		log.info(name)
		if not name:
			return
		filename= name+'.pickle'
		filepath= os.path.join(LIBRARIES_DIR, filename)#.decode("mbcs")
		open(filepath, 'w').close()
		LibraryDialog.libraryFiles.append(name)
		LibraryDialog.libraryFiles.sort()
		self.refreshLibraries(str= name)

	def onRename(self, evt):
		# Translators: Message displayed when renaming a library
		message= _('Enter new name please')
		# Translators: Title of dialog to enter new name.
		caption= _('rename')
		oldName= self.listBox.GetStringSelection()
		i= LibraryDialog.libraryFiles.index(oldName)
		LibraryDialog.libraryFiles.remove(oldName)
		newname= addLibrary(message, caption, oldName)
		log.info('newname: %s'%newname)
		if not newname or newname== oldName:
			LibraryDialog.libraryFiles.insert(i, oldName)
			return
		else:
			os.rename(os.path.join(LIBRARIES_DIR, oldName+'.pickle'), os.path.join(LIBRARIES_DIR, newname+'.pickle'))
			#log.info(LibraryDialog.libraryFiles)
			LibraryDialog.libraryFiles.append(newname)
			LibraryDialog.libraryFiles.sort()
			self.refreshLibraries(str= newname)

	def onRemove(self, evt):
		toRemove= self.listBox.GetStringSelection()
		i= self.listBox.GetSelection()
		if gui.messageBox(
		# Translators: Message displayed upon removing a library.
		_(u'Are you sure you want to remove {} library, this can not be undone?'.format(toRemove)),
		# Translators: Title of dialog.
		#_('Warning'), wx.NO|wx.YES)== wx.NO:
		_('Warning'), wx.ICON_QUESTION | wx.YES_NO)== wx.NO:
			return
		#path= os.path.abspath(os.path.join(CURRENT_DIR, '..', '..', toRemove+'.pickle')).decode("mbcs")
		#os.remove(path)
		os.remove(os.path.join(LIBRARIES_DIR, toRemove+'.pickle'))
		LibraryDialog.libraryFiles.remove(toRemove)
		sel= i if len(LibraryDialog.libraryFiles)>= i+2 else i-1
		self.refreshLibraries(i= sel)

	def refreshLibraries(self, str=None, i= None):
		'''
		@str: name of selected library
		@i: index of selected library
		'''
		self.Hide()
		self.listBox.Set(LibraryDialog.libraryFiles)
		if str:
			self.listBox.SetStringSelection(str)
		if i:
			self.listBox.SetSelection(i)
		self.Show()

	def onKillFocus(self, evt):
		library_name= self.listBox.GetStringSelection()
		if library_name== 'general':
			self.rename.Disable()
			self.remove.Disable()
		else:
			if not self.rename.IsEnabled() or not self.remove.IsEnabled():
				self.rename.Enable()
				self.remove.Enable()
		evt.Skip()

	def onOk(self, evt):
		log.info('under ok button')
		i= self.listBox.GetSelection()
		if i != -1:
			filename= self.libraryFiles[i]
			#dlg= LinkDialog(gui.mainFrame, filename)
			if  LinkDialog.currentInstance:
				gui.messageBox(
				# Translators: Message be displayed when a library dialog is already opened.
			_('A library dialog is already opened; Close it first please.'),
			# Translators: Title of dialog.
			_('information'))
				return
			else:
				wx.CallAfter(self.openLinkDialog, filename)
			self.Destroy()
		

	def openLinkDialog(self, filename):
		dialog= LinkDialog(gui.mainFrame, filename)
		LinkDialog.currentInstance= dialog

	def onClose(self, evt):
		self.Destroy()

if __name__== '__main__':
	x= wx.App()
	LibraryDialog(None)
	x.MainLoop()