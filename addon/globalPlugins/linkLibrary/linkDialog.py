# -*- coding: utf-8 -*-
#linkDialog.py
# Copyright 2019 ibrahim hamadeh, released under GPLv2.0
#graphical user interface for link dialog

import wx, gui
import webbrowser, os
import subprocess 
import queueHandler
import winVersion
import config
from .links import Link
#importing the getBrowsers function that retreaves the found browsers in the registry
from .getbrowsers import getBrowsers
browsersFound= getBrowsers()
from logHandler import log

import addonHandler
addonHandler.initTranslation()

def getLinkUrl(message, caption, link= None):
	''' Entring the source url of the link upon adding or editing a link.'''
	if not link:
		url= wx.GetTextFromUser(message, caption).strip()
	else:
		url= wx.GetTextFromUser(message, caption, link.url).strip()
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

class OpenWithMenu(wx.Menu):
	''' The menu that pops up when pressing openlink with button.'''
	def __init__(self, parentDialog, link):
		super(OpenWithMenu, self).__init__()

		self.link= link
		self.parentDialog= parentDialog

		#if in windows10, add a menu item for edge browser
		if winVersion.winVersionText.startswith('10'):
			edge= wx.MenuItem(self, -1, text= 'Microsoft Edge')
			self.Append(edge)
			self.Bind(wx.EVT_MENU, self.onEdge, edge)

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

	def onEdge(self, evt):
		url= self.link.url
		if url:
			url= 'http://'+url if url.startswith('www') else url
			os.startfile("microsoft-edge:{i}".format(i=url)) 
			self.parentDialog.checkCloseAfterActivatingALink()

#the popup menu class
class MyPopupMenu(wx.Menu):
	''' The menu that pops up upon right clicking on the list box.'''
	def __init__(self, parent, eventObjectId):
		super(MyPopupMenu, self).__init__()
        
		self.parent = parent
		self.eventObjectId= eventObjectId


		#Add A Link menu
		add= wx.MenuItem(self, -1, 
		# Translators: label obj menu items to add a link.
		_('Add A Link'))
		self.Append(add)
		self.Bind(wx.EVT_MENU, self.onAdd, add)

		#Edit Selected Link menu
		edit= wx.MenuItem(self, -1, 
		# Translators: label of menu items to edit a link.
		_('Edit Selected '))
		self.Append(edit)
		self.Bind(wx.EVT_MENU, self.onEdit, edit)

		#Remove Selected Link menu
		remove= wx.MenuItem(self, -1, 
		# Translators: label of menu items to remove a link.
		_('Remove Selected '))
		self.Append(remove)
		self.Bind(wx.EVT_MENU, self.onRemove, remove)

		#Remove All Links menu
		removeAll= wx.MenuItem(self, -1, 
		# Translators: label of menu items to remove all links.
		_('Remove All '))
		self.Append(removeAll)
		self.Bind(wx.EVT_MENU, self.onRemoveAll, removeAll)

	def onAdd(self, evt= None, link= None):
		#getting the url of the link
		url= getLinkUrl('Enter Link source(www...)', 'Url:', link)
		log.info('url: %s'%url)
		if not url: return

		# getting the label of the link.
		label=getLinkLabel('Enter Link Label Please', 'Link Label', link)
		log.info('label: %s'%label)
		if not label: return

		#getting the about of the link
		about= getLinkAbout("Write Something About The Link", "About", link)

		Link.add_link(url, label, about)
		self.parent.populateListBox(selected= label)
		#self.parent.focusAndSelect(selected= label)
		return True

	def onEdit(self, evt):
		listBox= self.parent.FindWindowById(self.eventObjectId)
		i= listBox.GetSelection()
		if i!= -1:
			label= self.parent.link_labels[i]
			l= Link.getLinkByLabel(label)
			Link.remove_link(l.url)
			edited= self.onAdd(link= l)
			#if the user cancelled editing the link, we should return it back to the dictionary and abort its removal.
			if not edited:
				Link.add_link(l.url, l.label, l.about)

	def onRemove(self, evt):
		listBox= self.parent.FindWindowById(self.eventObjectId)
		i= listBox.GetSelection()
		if i!= -1:
			label= self.parent.link_labels[i]
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
			index= i if len(self.parent.link_labels)>= i+2 else i-1
			if index >=0:
				#self.parent.populateListBox(selected= self.parent.link_labels[index])
				self.parent.populateListBox()
				listBox.SetSelection(index)
			else: self.parent.populateListBox()
			#self.parent.populateListBox()

	def onRemoveAll(self, evt):
		if gui.messageBox(
		# Translators: Message displayed when trying to remove all links.
		_('Are you sure you want to remove all links from this library?, this can not be undone.'),
		# Translators: Title of message box.
		_('Warning'),
		wx.YES|wx.NO|wx.ICON_QUESTION)== wx.NO:
			return
		Link.remove_allLinks()
		self.parent.populateListBox()
		self.Destroy()
		#self.parent.focusAndSelect()

class LinkDialog(wx.Dialog):
	#to insure that there is only one instance of LinkDialog class is running
	currentInstance= None

	def __init__(self, parent, filename, libraries_path):
		super(LinkDialog, self).__init__(parent, -1, title= filename, 
		size=(500, 300))
		self.filename= filename
		#sending the filename to the Link class
		Link.filename= filename + ".json"
		#Sending libraries path to the Link class
		Link.SAVING_DIR= libraries_path

		panel = wx.Panel(self, -1) 
		# Translators: Label for the list of links.
		listLabel= wx.StaticText(panel, -1, _("List Of Links"))
		self.listBox= wx.ListBox(panel, -1, style= wx.LB_SINGLE)

		# Translators: Label of about the link text control.
		aboutLabel = wx.StaticText(panel, -1, _("About The Link"))
		self.aboutText = wx.TextCtrl(panel, -1,
			   "Here is a looooooooooooooong line of text set in the control.\n\n"
			   "See that it wrapped, and that this line is after a blank",
			   size=(200, 100), style=wx.TE_MULTILINE|wx.TE_READONLY)

		self.showOrHideUrlButton= wx.Button(panel, -1,
		   # Translators: Label of toggle button that shows or hides the source url of the link.
		_("Show Source Url"))

		# Translators: Label of the text control that shows the url .
		urlLabel = wx.StaticText(panel, -1, _("Url:"))
		self.urlText = wx.TextCtrl(panel, -1, "", 
		size=(175, -1), style= wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_NO_VSCROLL|wx.TE_PROCESS_ENTER)
		#self.urlText.SetSelection(0, -1)

		# Translators: Label of open link with button.
		self.openLinkWithButton= wx.Button(panel, -1, label= _("Open Link With"))
		self.okButton= wx.Button(panel, id= wx.ID_OK, label= "")
		self.okButton.SetDefault()
		#Label of Close button.
		self.closeButton= wx.Button(panel, id= wx.ID_CANCEL, label= _("Close"))

		sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
		sizer.AddMany([listLabel, self.listBox, aboutLabel, self.aboutText, self.showOrHideUrlButton,urlLabel, self.urlText, self.openLinkWithButton, self.closeButton])
		panel.SetSizer(sizer)

		#make bindings
		#self.listBox.Bind(wx.EVT_KEY_UP, self.onOpenWithDefault)
		#self.Bind(wx.EVT_LISTBOX_DCLICK, self.onOpenWithDefault, self.listBox)
		self.listBox.Bind(wx.EVT_LISTBOX, self.onKillFocus)
		self.listBox.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.listBox.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
		#self.listBox.Bind(wx.EVT_SET_FOCUS, self.onKillFocus)
		self.Bind(wx.EVT_BUTTON, self.onShowOrHideUrl, self.showOrHideUrlButton)
		self.urlText.Bind(wx.EVT_TEXT_ENTER, self.onOpenWithDefault)
		self.Bind(wx.EVT_BUTTON, self.onOpenLinkWith, self.openLinkWithButton)
		self.Bind(wx.EVT_BUTTON, self.onOpenWithDefault, self.okButton)
		self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
		self.postInit()

	def postInit(self):
		self.populateListBox()
		self.urlText.Hide()
		self.okButton.Hide()
		self.Raise()
		self.Show()

	def populateListBox(self, selected= None):
		log.info('under populateListBox')
		Link.retreave_from_file()
		log.info(Link.myLinks)
		if not Link.myLinks:
			#LinkDialog.link_keys= []
			lst= []
			#self.listBox.Set(lst)
		else:
			try:
				lst = sorted([Link.myLinks[url]['label'] for url in Link.myLinks])
			except Exception as e:
				# Translators: Message displayed when getting an error trying to retreave links data
				gui.messageBox(_("Unable to load links data"), 
				# Translators: Title of message box
				_("Error"), wx.OK|wx.ICON_ERROR)
				#log.info('Error', exc_info=1)
				Link.myLinks= {}
				raise e

		self.Hide()
		self.link_labels= lst
		self.listBox.Set(lst)
		self.numberOfLinks= len(lst)
		self.SetTitle(u"{}({})".format(self.filename, self.numberOfLinks))
		if not lst:
			self.aboutText.Disable()
			[obj.Hide() for obj in (self.showOrHideUrlButton, self.urlText, self.openLinkWithButton)]
			self.Show()
			return
		if not selected:
			i= 0
			self.listBox.SetSelection(i)
		else:
			i= self.link_labels.index(selected)
			self.listBox.SetSelection(i)
		link= Link.getLinkByLabel(self.link_labels[i])
		self.showOrHideAboutControl(link.about)
		[obj.Show() for obj in (self.showOrHideUrlButton, self.openLinkWithButton)]
		self.Show()

	def OnRightDown(self, e):
#		print 'hi'
		obj= e.GetEventObject()
		id= obj.GetId()
		self.PopupMenu(MyPopupMenu(self, id), e.GetPosition())

	def onKillFocus(self, evt):
		log.info('under kill focus event')
		i= self.listBox.GetSelection()
		if i!= -1:
#		if i== -1:
			#self.aboutText.Disable()
			#self.showOrHideUrlButton.Hide()
			#self.showOrHideUrlButton.Disable()
			#self.urlText.Hide()
			#self.openLinkWithButton.Hide()
			#return
		#else:
			link= Link.getLinkByLabel(self.link_labels[i])
			if link:
				self.showOrHideAboutControl(link.about)
				if self.showOrHideUrlButton.GetLabel()== "Hide Source Url":
					self.showOrHideUrlButton.SetLabel("Show Source Url")
				self.showOrHideUrlButton.Show()
				#self.showOrHideUrlButton.Enable()
				self.urlText.Hide()
				self.openLinkWithButton.Show()
		evt.Skip()

	def onShowOrHideUrl(self, evt):
		i= self.listBox.GetSelection()
		link= Link.getLinkByLabel(self.link_labels[i])
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
			log.info('about is shown')
		else : 
			self.aboutText.Disable()
			log.info('about is hiddin')

	def onOpenWithDefault(self, evt):
		log.info('under onOpenWithDefault handler')
		#key_code = evt.GetKeyCode()
		#if key_code== wx.WXK_RETURN:
		i= self.listBox.GetSelection()
		if i!= -1:
			try:
				link= Link.getLinkByLabel(self.link_labels[i])
			except KeyError:
				pass
			else:
				#if link.url:
				#webbrowser.open(link.url)
				queueHandler.queueFunction(queueHandler.eventQueue, webbrowser.open, link.url)
				self.checkCloseAfterActivatingALink()

	def onOpenLinkWith(self, evt):
		log.info('under onOpenLinkWith handler')
		i= self.listBox.GetSelection()
		link= Link.getLinkByLabel(self.link_labels[i])
		if link:
			btn = evt.GetEventObject()
			pos = btn.ClientToScreen( (0,0) )
			self.PopupMenu(OpenWithMenu(self, link), pos)

	def checkCloseAfterActivatingALink(self):
		if  config.conf["linkLibrary"]["closeDialogAfterActivatingALink"]:
			if Link.myLinks:
				Link.save_to_file()
			wx.CallLater(4000, self.Destroy)

	def onClose(self, evt):
		log.info('under onClose') 
		if Link.myLinks:
			Link.save_to_file()
		self.Destroy()
