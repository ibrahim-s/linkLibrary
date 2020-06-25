#getbrowsers.py
# Copyright 2019 ibrahim hamadeh, released under GPLv2.0.
# See the file COPYING for more details.
#This module is aimed to get several browsers if found in the registry and their path.

import os
import sys

# for compatibility with python3
try:
	import winreg as _winreg
except ImportError:
	import _winreg

#these are the keys that we are going to look for in the registry
exeLabels= {
	'firefox.exe': 'Firefox', 
	'chrome.exe': 'Google Chrome', 
	'iexplore.exe': 'Internet Explorer', 
	'opera.exe': 'Opera', 
	'seamonkey.exe': 'Seamonkey', 
	'wyzo.exe': 'Wyzo', 
	'waterfox.exe': 'Waterfox',
	'msedge.exe': 'Edge Chromium',
	'brave.exe': 'Brave'
}

def getKeyRegBrowsers(base_key, sub_key):
	"""sub_key is one of the main keys in the registry, or defined constants in _winreg module
	sub_key is the sub key in  the registry under which executable labels is found
	this function will return a list of tuples, consisting of the browser label if present and its path.""" 
	foundBrowsers=[]
	try:
		key= _winreg.OpenKey(base_key, sub_key)
		i=0
		while True:
			foundKey= _winreg.EnumKey(key, i)
			if foundKey.lower() in exeLabels:
				key2= _winreg.OpenKey(base_key, os.path.join(sub_key, foundKey))
				#_winreg.EnumValue(key2, 0) returns a tuple of three elements, path is the second.
				foundBrowsers.append((exeLabels[foundKey.lower()], _winreg.EnumValue(key2, 0)[1]))
			i+=1
	except WindowsError:
		pass
	return foundBrowsers

def getBrowsers():
	"""returns a list of browsers and their path in both
	HKEY_LOCAL_MACHINE an HKEY_CURRENT_USER main keys in the registry."""
	return getKeyRegBrowsers(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths')+ getKeyRegBrowsers(_winreg.HKEY_CURRENT_USER,r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths')
