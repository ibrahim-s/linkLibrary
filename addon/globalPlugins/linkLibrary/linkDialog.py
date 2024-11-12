# -*- coding: utf-8 -*-
# linkDialog.py
# Copyright 2019 ibrahim hamadeh, released under GPLv2.0
# See the file COPYING for more details.
# Graphical user interface for link dialog

import wx, gui
import webbrowser, os
import subprocess 
import json
import re
import queueHandler
import config
import api
from .links import Link
#importing the getBrowsers function that retreaves the found browsers in the registry
from .getbrowsers import getBrowsers
from logHandler import log

import addonHandler
addonHandler.initTranslation()

browsersFound= getBrowsers()

def getLinkUrl(message, caption, link= None):
	''' Entring the source url of the link upon adding or editing a link.'''
	if not link:
		url= wx.GetTextFromUser(message, caption).strip().rstrip('/')
	else:
		url= wx.GetTextFromUser(message, caption, link.url).strip().rstrip('/')
	if not url:
		return 
	else:
		linkObj= Link.getLinkByUrl(url)
		if linkObj:
			gui.messageBox(
			# Translators: message displayed when the url is present for another link.
			_('This url is for {}; please enter another one').format(linkObj.label), 
			_('Warning'))
			return getLinkUrl(message, caption, link)
		return url

def getLinkLabel(message, caption, link= None):
	''' Entring the label of the link upon adding or editing a link.'''
	if not link:
		label= wx.GetTextFromUser(message, caption).strip()
	else:
		label= wx.GetTextFromUser(message, caption, link.label).strip()
	if not label:
		return label
	else:
		linkObj= Link.getLinkByLabel(label)
		if linkObj:
			gui.messageBox(
			# Translators: message displayed when the label is present for another link.
			_('This label({}) is chosen for {}; please enter another one').format(linkObj.label, linkObj.url), 
			_('Warning'))
			return getLinkLabel(message, caption, link)
		return label

def getLinkAbout(message, caption, link= None):
	''' Entering the about or some discription about the link upon adding or editing one.'''
	dlg= wx.TextEntryDialog(None, message, caption, style= wx.OK | wx.CANCEL|wx.TE_MULTILINE)
	if link:
		dlg.SetValue(link.about)
	dlg.ShowModal()
	result= dlg.GetValue().strip()
	return result

def isSublibrary(name):
	''' use regular expression to know if the name ends with sub library suffix.'''
	pattern = r'\([^()]+\)$'
	result= re.search(pattern, name)
	return result
def getSublibraryName(name):
	''' use regular expression to get pure name without sub library suffix.'''
	pattern = r'\([^()]+\)$'
	result= re.split(pattern, name)[0]
	return result

class OpenWithMenu(wx.Menu):
	''' The menu that pops up when pressing openlink with button
	items of this menu are the labels of the browsers found on computer.
	'''
	def __init__(self, parentDialog, link):
		super(OpenWithMenu, self).__init__()

		self.link= link
		self.parentDialog= parentDialog

		#Add menu items for several browsers found in the registry
		#browsersFound is a list of tuples, each tuple consists of the browser name and it's executable path.
		for label, executable_path in browsersFound:
			item= wx.MenuItem(self, -1, label)
			self.Append(item)
			self.Bind(wx.EVT_MENU, lambda evt , args=executable_path : self.onOpen(evt, args), item)

	def onOpen(self, evt, executable_path):
		url= self.link.url
		if url:
			subprocess.Popen(executable_path+' '+url)
			self.parentDialog.checkCloseAfterActivatingALink()

#the popup menu class
class MyPopupMenu(wx.Menu):
	''' The menu that pops up upon right clicking on the list box.'''
	def __init__(self, parent, eventObjectId):
		super(MyPopupMenu, self).__init__()
        
		self.parent = parent
		self.eventObjectId= eventObjectId
		self.listBox= self.parent.FindWindowById(self.eventObjectId)
		# name of class of parent dialog, 'LinkDialog' or 'LinkSublibrary'.
		self.className= self.parent.__class__.__name__ 
		self._index = self.listBox.GetSelection()
		if self._index!= -1:
			self._label = self.listBox.GetString(self._index)
		#log.info(f'_index: {self._index}, _label: {self._label}')

		# if it is a sub library,we should not allow to add sub libraries to it.
		# Add sub library menu should appear only if it is not a sub library.
		if self.className!= 'LinkSublibrary':
		#Add sub library  menu
			self.addSublibrary= wx.MenuItem(self, -1, 
			# Translators: label of menu items to add a sub library.
			_('Add Sub library'))
			self.Append(self.addSublibrary)
			self.Bind(wx.EVT_MENU, self.onAddSublibrary, self.addSublibrary)

		if self._index!= -1 and isSublibrary(self._label):
			#Rename sub library  menu
			self.renameSublibrary= wx.MenuItem(self, -1, 
			# Translators: label of menu items to rename a sub library.
			_('Rename Sub library'))
			self.Append(self.renameSublibrary)
			self.Bind(wx.EVT_MENU, self.onRenameSublibrary, self.renameSublibrary)

			#Remove sub library  menu
			self.removeSublibrary= wx.MenuItem(self, -1, 
			# Translators: label of menu items to remove a sub library.
			_('Remove Sub library'))
			self.Append(self.removeSublibrary)
			self.Bind(wx.EVT_MENU, self.onRemoveSublibrary, self.removeSublibrary)

		#Add A Link menu
		add= wx.MenuItem(self, -1, 
		# Translators: label obj menu items to add a link.
		_('Add A Link'))
		self.Append(add)
		self.Bind(wx.EVT_MENU, self.onAdd, add)

		if self._index!= -1 and not isSublibrary(self._label):
			#Edit Selected Link menu
			self.edit= wx.MenuItem(self, -1, 
			# Translators: label of menu items to edit a link.
			_('Edit Selected '))
			self.Append(self.edit)
			self.Bind(wx.EVT_MENU, self.onEdit, self.edit)

			#add a subMenu for moving a link
			# We want to append to this menu library names.
			# list of names of major libraries.
			libraryNames= LinkDialog.libraryFiles
			#log.info(f'activeLibrary: {LinkDialog.activeLibrary}')
			libraryMenus= (name for name in libraryNames if name!= LinkDialog.activeLibrary)
			self.subMenu= wx.Menu()
			# appending library menus to subMenu.
			for label in libraryMenus:
				item= self.subMenu.Append(wx.ID_ANY, label)
				self.Bind(wx.EVT_MENU, lambda evt , args=label : self.onMoveLink(evt, args), item)
			self.AppendSubMenu(self.subMenu, 
			# Translators: label obj subMenu items for moving a link.
			_('Move Link To'))

			# if we are in sub library, we will make menu of the other sublibraries, and prepend it to library menus, under name of the library in which the are present.
			# subMenu2 is the menu to append to it sub libraries.
			self.subMenu2= wx.Menu()
			# make submenu only if we have more than 1 sublibrary.
			# or it is a major library, but has sub libraries.
			hasSublibrary= self.parent.sublibraries
			#log.info(f'hasSublibrary: {hasSublibrary}')
			# if we are in sub library, return back the parent libraries, and append it to main menu.
			if self.className== 'LinkSublibrary' :
				extraItem=self.subMenu.Append(wx.ID_ANY, self.parent.parent.filename)
				self.Bind(wx.EVT_MENU, lambda evt,arg= self.parent.parent.filename: self.onMoveLink(evt, arg), extraItem)
			# in these two cases, we want to make a sub menu.
			if (self.className== 'LinkSublibrary' and len(os.listdir(Link.sublibraries_path))>1) or hasSublibrary:
				if self.className== 'LinkSublibrary':
					activeSublibraryName= self.parent.filename
					sublibraryNames= filter(lambda x: x!= activeSublibraryName,[name.split('.json')[0] for name in os.listdir(Link.sublibraries_path)])
				# we are in major library, but has sub libraries.
				elif hasSublibrary:
					sublibraryNames= [getSublibraryName(label) for label in hasSublibrary]
				for label in sublibraryNames:
					item= self.subMenu2.Append(wx.ID_ANY, label)
					self.Bind(wx.EVT_MENU, lambda evt , args=label : self.onMoveLink(evt, args), item)
				# insert subMenu2 as first item in subMenu.
				# label of subMenu2
				subMenu2Label= self.parent.filename if hasSublibrary else self.parent.parent.filename
				self.subMenu.Prepend(wx.ID_ANY, subMenu2Label, self.subMenu2)

			#Remove Selected Link menu
			remove= wx.MenuItem(self, -1, 
			# Translators: label of menu items to remove a link.
			_('Remove Selected '))
			self.Append(remove)
			self.Bind(wx.EVT_MENU, self.onRemove, remove)

			#Remove All Links menu
			removeAll= wx.MenuItem(self, -1, 
			# Translators: label of menu items to remove all links.
			_('Remove All Links'))
			self.Append(removeAll)
			self.Bind(wx.EVT_MENU, self.onRemoveAllLinks, removeAll)

	def onAddSublibrary(self, evt):
		libraryName= self.parent.filename
		sublibrary_path= self.parent.sublibrariesPath
		#log.info(f'LibraryName: {libraryName}')
		# Translators: Message displayed when adding a sublibrary.
		message= _('Enter sublibrary name please')
		# Translators: Title of dialog.
		caption= _('Add subLibrary for {}').format(libraryName)
		while True:
			name=wx.GetTextFromUser(message, caption).strip()
			#log.info(f'name entered: {name}')
			if not name:
				return
			if not os.path.isdir(sublibrary_path):
				os.mkdir(sublibrary_path)
				# in self.sublibraries the label has (Sub library) suffix.
			if name in [getSublibraryName(label) for label in self.parent.sublibraries]:
				gui.messageBox(
				# Translators: message displayed when the name is present for another sub library.
				_('This name is already present for another sub library, enter another name please'), 
				# Translators: Title of messagebox.
				_('Warning'))
			else:
				break
		filename= api.filterFileName(name)+'.json'
		filepath= os.path.join(sublibrary_path, filename)
		#log.info('filepath to add: %s'%filepath)
		try:
			with open(filepath, 'w') as f:
				f.write("{}")
		except Exception as e:
			raise e
		# refresh main or background window of libraries
		#nameOfLibraryWithSuffix = libraryName+ '(Has sub library)'
		indx= self.parent.parent.listBox.GetSelection()
		self.parent.parent.refreshLibraries(i=indx)
		# Reflect the changes in self.sublibraries list
		self.parent.getSublibraries(self.parent.sublibrariesPath)
		indx=self.parent.sublibraryPureNames.index(name)
		self.parent.populateListBox()
		self.listBox.SetSelection(indx)

	def onRenameSublibrary(self, evt):
		sublibraryPath= self.parent.sublibrariesPath
		# Translators: Message displayed when renaming a sub library
		message= _('Enter new name please')
		# Translators: Title of dialog to enter new name.
		caption= _('Rename sub library')
		oldName= getSublibraryName(self._label)
		while True:
			newName= wx.GetTextFromUser(message, caption, oldName).strip()
			if not newName or newName== oldName:
				return
			try:
				os.rename(os.path.join(sublibraryPath, oldName+'.json'), os.path.join(sublibraryPath, api.filterFileName(newName) +'.json'))
			except FileExistsError:
				gui.messageBox(
				# Translators: message displayed when the name is present for another sub library.
				_('This name is already present for another sub library, enter another name please'), 
				# Translators: Title of messagebox.
				_('Warning'))
			else:
				break
		#log.info(f'newName: {newName}')
		# Reflect the change in sublibraries list
		self.parent.getSublibraries(self.parent.sublibrariesPath)
		indx= self.parent.sublibraryPureNames.index(newName)
		self.parent.populateListBox()
		self.listBox.SetSelection(indx)

	def onRemoveSublibrary(self, evt):
		sublibraryPath= self.parent.sublibrariesPath
		filename= getSublibraryName(self._label)
		# number of items or libraries in the list.
		numItems= self.listBox.GetCount()
		if gui.messageBox(
		# Translators: Message displayed upon removing a sub library.
		_('Are you sure you want to remove the sub library {}, this can not be undone?').format(filename),
		# Translators: Title of dialog.
		_('Warning'), wx.ICON_QUESTION | wx.YES_NO)== wx.NO:
			return
		os.remove(os.path.join(sublibraryPath, filename+'.json'))
		if len([filename for filename in os.listdir(sublibraryPath) if filename.endswith('.json')])== 0:
			os.rmdir(sublibraryPath)
			libraryDialog= self.parent.parent
			# No sub libraries, then stand on the bare name of library in main window.
			libraryDialog.refreshLibraries(os.path.basename(sublibraryPath))
		# reflect the changes in self.sublibraries
		self.parent.getSublibraries(self.parent.sublibrariesPath)
		sel= self._index if self._index!= numItems-1 else self._index-1
		if sel>= 0:
			self.parent.populateListBox()
			self.listBox.SetSelection(sel)
		else:
			self.parent.populateListBox()

	def onAdd(self, evt= None, link= None):
		''' Adding a link '''
		# Translators: getting the url of the link
		url= getLinkUrl(_("Enter Link source(www...)"),
		# Translators: title of dialog.
		_("Url:"), link)
		#log.info('url: %s'%url)
		if not url: return

		# Translators: getting the label of the link.
		label=getLinkLabel(_("Enter Link Label Please"),
		# Translators: title of dialog.
		_("Link Label"), link)
		#log.info('label: %s'%label)
		if not label: return

		# Translators: getting the about of the link
		about= getLinkAbout(_("Write Something About The Link"),
		# Translators: title of dialog.
		_("About"), link)
		#log.info(f'link to be added: {url}, {label}, {about}')
		Link.add_link(url, label, about)
		self.parent.populateListBox(selected= label)
		return True

	def onEdit(self, evt):
		listBox= self.listBox
		i= listBox.GetSelection()
		if i!= -1:
			label= listBox.GetString(i)
			l= Link.getLinkByLabel(label)
			Link.remove_link(l.url)
			edited= self.onAdd(link= l)
			#if the user cancelled editing the link, we should return it back to the dictionary and abort its removal.
			if not edited:
				Link.add_link(l.url, l.label, l.about)

	def onMoveLink(self, event, menuItem):
		#log.info(f'menuItem: {menuItem}')
		menu = event.GetEventObject()
		#l=[self, self.subMenu, self.subMenu2]
		#for x in l:
			#if menu== x:
				#log.info(l.index(x))
		# menuItem is the menu item or library name that we want to move the link to it.
		listBox= self.listBox
		i= listBox.GetSelection()
		if i== -1:
			return
		linkLabel= listBox.GetString(i)
		#log.info(f'linkLabel: {linkLabel}')
		link= Link.getLinkByLabel(linkLabel)
		libraryFileName= menuItem+ '.json'
		if self.className== 'LinkSublibrary' and menu== self.subMenu and self.parent.parent.filename== menuItem:
			self.moveToParentLibrary(link, linkLabel, menuItem, i)
			return
		if self.className== 'LinkSublibrary' and menu== self.subMenu and self.parent.parent.filename!= menuItem:
		# we are in sub library, and want to move the link to major library.
			saving_path= os.path.split(Link.SAVING_DIR)[0]
		elif self.className!= 'LinkSublibrary' and menu== self.subMenu2:
		# we are in library dialog, and want to move the link to sub library.
			saving_path= os.path.join(Link.SAVING_DIR, self.parent.filename)
		else:
			saving_path= Link.SAVING_DIR
		#log.info(f'saving_path: {saving_path}')
		# retreaving library data
		try:
			with open(os.path.join(saving_path, libraryFileName), encoding= 'utf-8') as f:
				libraryDict= json.load(f)
			if link.url in libraryDict:
				if gui.messageBox(
				# Translators: Message displayed when trying to move a link already present in the other library.
				_("This link is already present in {library} library, under {label} label;\n"
				" Do you still want to replace it with the one you are about to move?.").format(library= menuItem, label= libraryDict[link.url]['label']),
				# Translators: Title of message box.
				_('Warning'),
				wx.YES|wx.NO|wx.ICON_QUESTION)== wx.NO:
					return

			libraryDict[link.url]= {"label": link.label, "about": link.about}
			with open(os.path.join(saving_path, libraryFileName), 'w', encoding= 'utf-8') as f:
				json.dump(libraryDict, f, ensure_ascii= False, indent= 4)
		except Exception as e:
			# Translators: Message displayed when getting an error trying to move a link from one library to another.
			gui.messageBox(_("Unable to move the link to another library"), 
			# Translators: Title of message box
			_("Error"), wx.OK|wx.ICON_ERROR)
			raise e
			return
		# We have moved the link, now we want to remove it from current library.
		Link.remove_link(link.url)
		# index of the link to be selected and focused on
		index= i if listBox.GetCount() >= i+2 else i-1
		self.parent.populateListBox()
		#log.info('after populating the list box ...')
		if index >=0:
			listBox.SetSelection(index)

	def moveToParentLibrary(self, link, linkLabel, menuItem, i):
		#i is the index of link to be moved
		# if we have moved the link from the current sub library to parent library, and parent library opened in background
		# writing the link to file is not appropriate, so we will add the link to myLinks dictionary in Link class
		if link.url in Link.myLinks:
			if gui.messageBox(
			# Translators: Message displayed when trying to move a link already present in the other library.
			_("This link is already present in {library} library, under {label} label;\n"
			" Do you still want to replace it with the one you are about to move?.").format(library= menuItem, label= Link.myLinks[link.url]['label']),
			# Translators: Title of message box.
			_('Warning'),
			wx.YES|wx.NO|wx.ICON_QUESTION)== wx.NO:
				return
		Link.myLinks[link.url]= {"label": link.label, "about": link.about}
		Link.remove_link(link.url)
		# refresh parent library in the background
		indx= LinkDialog.currentInstance.listBox.GetSelection()
		# change Link class attributes, to work for parent major library.
		Link.filename= menuItem + '.json'
		Link.changeClassAttributes(default= True)
		#log.info(f'Link.SAVING_DIR: {Link.SAVING_DIR}')
		LinkDialog.currentInstance.populateListBox()
		# return the index where it was before 
		LinkDialog.currentInstance.listBox.SetSelection(indx)
		# return Link class attributes, to work for current sub library.
		Link.isSublibrary= True
		Link.filename= self.parent.filename+ '.json'
		Link.sublibraries_path= self.parent.parent.sublibrariesPath
		Link.changeClassAttributes(default= False)
		# index of the link to be selected and focused on
		index= i if self.listBox.GetCount() >= i+2 else i-1
		self.parent.populateListBox()
		#log.info('after populating the list box in sub library...')
		if index >=0:
			self.listBox.SetSelection(index)

	def onRemove(self, evt):
		listBox= self.listBox
		i= listBox.GetSelection()
		if i!= -1:
			label= listBox.GetString(i)
			l= Link.getLinkByLabel(label)
			if gui.messageBox(
			# Translators: Message displayed when trying to remove a link.
			_('Are you sure you want to remove the link labeled {} from the library?, this can not be undone.').format(l.label),
			# Translators: Title of message box.
			_('Warning'),
			wx.YES|wx.NO|wx.ICON_QUESTION)== wx.NO:
				return
			Link.remove_link(l.url)
			# index of the link to be selected and focused on
			index= i if listBox.GetCount()>= i+2 else i-1
			if index >=0:
				self.parent.populateListBox()
				listBox.SetSelection(index)
			else:
				self.parent.populateListBox()

	def onRemoveAllLinks(self, evt):
		''' Remove all links.'''
		listBox= self.listBox
		i= listBox.GetSelection()
		if i== -1:
			return
		if gui.messageBox(
		# Translators: Message displayed when trying to remove all links.
		_('Are you sure you want to remove all links from this library?, this can not be undone.'),
		# Translators: Title of message box.
		_('Warning'),
		wx.YES|wx.NO|wx.ICON_QUESTION)== wx.NO:
			return
		Link.remove_allLinks()
		self.parent.populateListBox()

class LinkDialog(wx.Dialog):
	''' Dialog of library that contains list of links, and it may contain also sub libraries.
	sub libraries will reside in the top of listBox, and they will have (Sub library) suffix.'''
	#to insure that there is only one instance of LinkDialog class is running
	currentInstance= None

	def __init__(self, parent, filename, libraries_path):
		super(LinkDialog, self).__init__(parent, -1, title= filename, 
		size=(500, 400))
		self.parent= parent
		self.sublibrariesPath = os.path.join(libraries_path, filename)
		# Sub libraries names with sub library suffix. 
		self.sublibraries= self.getSublibraries(self.sublibrariesPath) 
		# when the function self.getSublibraries is executed it will populate sublibraryPureNames.
		self.sublibraryPureNames= [] #name of sublibraries without suffix
		self.filename= filename
		#sending the filename to the Link class
		Link.filename= filename + ".json"

		panel = wx.Panel(self, -1) 
		# Translators: Label for search or filter control.
		filterLabel= wx.StaticText(panel, label= _("Filter by:"))
		self.filterControl= wx.TextCtrl(panel, -1, )

		# Translators: Label for the list of links.
		listLabel= wx.StaticText(panel, -1, _("List Of Links"))
		self.listBox= wx.ListBox(panel, -1, style= wx.LB_SINGLE)

		# Translators: Label of about the link text control.
		aboutLabel = wx.StaticText(panel, -1, _("About The Link"))
		self.aboutText = wx.TextCtrl(panel, -1,
			   size=(200, 100), style=wx.TE_MULTILINE|wx.TE_READONLY)

		self.showOrHideUrlButton= wx.Button(panel, -1,
		   # Translators: Label of toggle button that shows or hides the source url of the link.
		_("Show Source Url"))

		# Translators: Label of the text control that shows the url .
		urlLabel = wx.StaticText(panel, -1, _("Url:"))
		self.urlText = wx.TextCtrl(panel, -1, "", 
		size=(175, -1), style= wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_NO_VSCROLL|wx.TE_PROCESS_ENTER)

		# Translators: Label of open link with button.
		self.openLinkWithButton= wx.Button(panel, -1, label= _("Open Link With"))
		# Translators: Label of OK button.
		self.okButton= wx.Button(panel, id= wx.ID_OK, label= _("OK"))
		self.okButton.SetDefault()
		#Label of cancel button.
		self.cancelButton= wx.Button(panel, id= wx.ID_CANCEL, label= _("Cancel"))

		sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
		sizer.AddMany([filterLabel, self.filterControl, listLabel, self.listBox, aboutLabel, self.aboutText, self.showOrHideUrlButton,urlLabel, self.urlText, self.openLinkWithButton, self.okButton, self.cancelButton])
		panel.SetSizer(sizer)

		#make bindings
		self.filterControl.Bind(wx.EVT_TEXT, self.onFilterTextChange)
		self.listBox.Bind(wx.EVT_LISTBOX, self.onKillFocus)
		#self.listBox.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.listBox.Bind(wx.EVT_CONTEXT_MENU, self.OnRightDown)
		#wx.EVT_CONTEXT_MENU is used in NVDA 2021.1,for wx.EVT_RIGHT_DOWN seized to work.
		self.listBox.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
		self.Bind(wx.EVT_BUTTON, self.onShowOrHideUrl, self.showOrHideUrlButton)
		self.urlText.Bind(wx.EVT_TEXT_ENTER, self.onOpenWithDefault)
		self.Bind(wx.EVT_BUTTON, self.onOpenLinkWith, self.openLinkWithButton)
		self.Bind(wx.EVT_BUTTON, self.onOpenWithDefault, self.okButton)
		self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancelButton)
		self.postInit()

	def getSublibraries(self, sublibrariesPath):
		''' Get name of sub libraries  with (Sub library ) suffix
		return type list.'''
		if not os.path.isdir(sublibrariesPath):
			sublibraries= []
		else:
			foundFiles= [os.path.splitext(f) for f in os.listdir(sublibrariesPath)]
			# foundFiles is a list of tuples, first element of the tuple is the name of file and the second is it's extension
			sublibraryPureNames= sorted([name for name, ext in foundFiles if ext== '.json'], key= str.lower)
			# Translators: Suffix of sub library label.
			sublibrarySuffix= _("Sub library")
			sublibraries= sorted([f'{name}({sublibrarySuffix})' for name, ext in foundFiles if ext== '.json'], key= str.lower)
			self.sublibraryPureNames= sublibraryPureNames
		self.sublibraries = sublibraries
		#log.info(f'sublibraries: {sublibraries}')
		return sublibraries

	def postInit(self):
		self.populateListBox()
		self.urlText.Hide()
		self.Raise()
		self.listBox.SetFocus()
		self.Show()

	def populateListBox(self, selected: str=None, filteredList= None):
		#log.info('under populateListBox')
		Link.retreave_from_file()
		# get linksDictionary from Link class, it may be myLinksfor libraries or sublibraryLinks for sublibraries.
		linksDictionary= Link.get_linksDictionary()
		#log.info(f'linksDictionary during populateListBox: {linksDictionary}')
		if filteredList is None and not linksDictionary:
			lst= []
		elif filteredList is not None:
			# it may be an empty list or not empty list.
			lst= filteredList
		else:
			try:
				lst = sorted([linksDictionary[url]['label'] for url in linksDictionary], key= lambda s: s.lower())
			except Exception as e:
				# Translators: Message displayed when getting an error trying to retreave links data
				gui.messageBox(_("Unable to load links data"), 
				# Translators: Title of message box
				_("Error"), wx.OK|wx.ICON_ERROR)
				if not Link.isSublibrary:
					Link.myLinks= {}
				else: 
					Link.sublibraryLinks= {}
				raise e

		self.Hide()
		self.link_labels= lst
		self.listBox.Set(lst)
		if self.sublibraries:
			self.listBox.InsertItems(self.sublibraries, 0)
		self.numberOfLinks= len(lst)
		# Translators: suffix of title.
		suffix= _("link") if self.numberOfLinks== 1 else _("links")
		self.SetTitle("{}({} {})".format(self.filename, self.numberOfLinks, suffix))
		if self.listBox.IsEmpty():
			self.aboutText.Disable()
			[obj.Hide() for obj in (self.showOrHideUrlButton, self.urlText, self.openLinkWithButton)]
			self.Show()
			return
		if not selected:
			i= 0
			if self.sublibraries:
				self.aboutText.Disable()
				[obj.Hide() for obj in (self.showOrHideUrlButton, self.urlText, self.openLinkWithButton)]
		else:
			# selected is the label of selected link.
			i= self.link_labels.index(selected)
			# adjusting the selected index, by adding the len of sublibraries in the listBox.
			if self.sublibraries:
				i= i+ len(self.sublibraries)
		self.listBox.SetSelection(i)
		#log.info(f'i: {i}')
		link= Link.getLinkByLabel(self.listBox.GetString(i))
		# it may be a sub library and not a link
		if link:
			self.showOrHideAboutControl(link.about)
			[obj.Show() for obj in (self.showOrHideUrlButton, self.openLinkWithButton)]
		self.Show()

	def onFilterTextChange(self, evt):
		'''Searching for text entered, in list of links of present library.'''
		text= self.filterControl.Value
		# In case we entered something, and deleted it.
		if not text:
			self.populateListBox()
			return
		text= text.lower()
		labels_list= []
		#log.info(f'text= {text}')
		myLinks= Link.myLinks if not Link.isSublibrary else Link.sublibraryLinks
		for url in myLinks:
		# Removing the url protocol, or prefex of url.
			urlBase= re.sub(r"(?:https?://|ftp://|www.)", "", url)
			label= myLinks[url]['label']
			# We search for text in main part of url, or in label.
			if any(text in s.casefold() for s in (label, urlBase)):
				labels_list.append(label)
		#log.info(f'labels_list: {labels_list}')
		if labels_list:
			labels_list= sorted(labels_list, key= str.lower)
		self.populateListBox(filteredList= labels_list)

	def OnRightDown(self, evt):
		obj= evt.GetEventObject()
		id= obj.GetId()
		menu= MyPopupMenu(self, id)
		self.PopupMenu(menu, evt.GetPosition())
		menu.Destroy()
		#log.info('destroying context menu')

	def onKillFocus(self, evt):
		#log.info('under kill focus event')
		i= self.listBox.GetSelection()
		if i!= -1:
			label= self.listBox.GetString(i)
			if isSublibrary(label):
				#log.info(f'item is sub library named {label}')
				self.aboutText.Disable()
				[obj.Hide() for obj in (self.showOrHideUrlButton, self.urlText, self.openLinkWithButton)]
				return
			link= Link.getLinkByLabel(label)
			if link:
				#log.info(f'link: {link}-under onKillFocus')
				self.showOrHideAboutControl(link.about)
				if self.showOrHideUrlButton.GetLabel()== "Hide Source Url":
					self.showOrHideUrlButton.SetLabel("Show Source Url")
				self.showOrHideUrlButton.Show()
				self.urlText.Hide()
				self.openLinkWithButton.Show()
		evt.Skip()

	def onShowOrHideUrl(self, evt):
		label= self.listBox.GetStringSelection()
		#log.info(f'label: {label} -under showOrHideUrlButton')
		link= Link.getLinkByLabel(label)
		if self.showOrHideUrlButton.GetLabel()== "Show Source Url":
			self.urlText.SetValue(link.url)
			self.urlText.SetSelection(0, -1)
			self.urlText.Show()
			self.urlText.SetFocus()
			self.showOrHideUrlButton.SetLabel("Hide Source Url")
		else:
			self.urlText.Hide()
			self.showOrHideUrlButton.SetLabel("Show Source Url")

	def showOrHideAboutControl(self, value):
		if value: # The about text control has some information about the link.
			self.aboutText.SetValue(value)
			self.aboutText.SetSelection(0, -1)
			self.aboutText.Enable()
			#log.info('about is shown')
		else : 
			self.aboutText.Disable()
			#log.info('about is hiddin')

	def onOpenWithDefault(self, evt):
		#log.info('under onOpenWithDefault handler')
		i= self.listBox.GetSelection()
		if i== -1:
			return
		label= self.listBox.GetString(i)
		if isSublibrary(label):
			self.openSublibrary(label)
		else:
			try:
				link= Link.getLinkByLabel(label)
			except KeyError:
				pass
			else:
				queueHandler.queueFunction(queueHandler.eventQueue, webbrowser.open, link.url, new=2)
				self.checkCloseAfterActivatingALink()

	def openSublibrary(self, name):
		name= getSublibraryName(name)
		Link.isSublibrary= True
		Link.sublibraries_path= self.sublibrariesPath
		Link.changeClassAttributes(default= False)
		if LinkSublibrary.sublibraryInstance:
			gui.messageBox(
			# Translators: Message displayed if another sub library is opened.
			_("Another sub library is opened, close it first please"),
			# Translators: title of message box.
			_("Warning")
			)
			return
		d=LinkSublibrary(self, name, self.sublibrariesPath)
		LinkSublibrary.sublibraryInstance = d

	def onOpenLinkWith(self, evt):
		#log.info('under onOpenLinkWith handler')
		i= self.listBox.GetSelection()
		link= Link.getLinkByLabel(self.listBox.GetString(i))
		if link:
			btn = evt.GetEventObject()
			pos = btn.ClientToScreen( (0,0) )
			menu= OpenWithMenu(self, link)
			self.PopupMenu(menu, pos)
			menu.Destroy()
			#log.info('destroying openWith popup menu')

	def checkCloseAfterActivatingALink(self):
		if  config.conf["linkLibrary"]["afterActivatingLink"]== 0:
			return
		if Link.myLinks:
			Link.save_to_file()
		if  config.conf["linkLibrary"]["afterActivatingLink"]== 1:
			wx.CallLater(4000, self.Destroy)
		elif  config.conf["linkLibrary"]["afterActivatingLink"]== 2:
			wx.CallLater(4000, self.GetParent().Destroy)

	def onCancel(self, evt):
		#log.info('under onClose') 
		if Link.myLinks:
			Link.save_to_file()
		self.Destroy()

class LinkSublibrary(LinkDialog):
	sublibraryInstance= None
	def __init__(self, parent, filename, sublibrariesPath):
		super(LinkSublibrary, self).__init__(parent, filename, sublibrariesPath)
		#		size=(500, 400))
		self.parent= parent
		self.sublibraries= False
		self.sublibraryPureNames= None

	def checkCloseAfterActivatingALink(self):
		''' overide the parent method, to deal with sub libraries. '''
		if  config.conf["linkLibrary"]["afterActivatingLink"]== 0:
			return
		self.onCancel(None)
		if  config.conf["linkLibrary"]["afterActivatingLink"]== 1:
			pass
		elif  config.conf["linkLibrary"]["afterActivatingLink"]== 2:
			if Link.myLinks:
				wx.CallLater(2000, Link.save_to_file())
				wx.CallLater(4000, self.parent.GetParent().Destroy)

	def onCancel(self, evt):
		#log.info('under onClose') 
		if Link.sublibraryLinks:
			Link.save_to_file()
		Link.filename= self.parent.filename + '.json'
		#log.info(f'self.parent.filename: {self.parent.filename}')
		Link.changeClassAttributes()
		self.Destroy()
