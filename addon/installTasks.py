# linkLibrary 
# required to keep or reserve files already present 
# Borrowed from Golden Cursor addon, thanks to people behind it.

#import addonHandler
import os
from logHandler import log
#import shutil

def onInstall():
	userPath= os.path.expanduser('~')
	addon_data_path= os.path.join(userPath, "linkLibrary-addonFiles")
	if not os.path.exists(addon_data_path):
		try:
			os.mkdir(addon_data_path)
			open(os.path.join(addon_data_path, "general.pickle"), 'w').close()
		except Exception as e:
			log.info('under except in install task')
			raise e