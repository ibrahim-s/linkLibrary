#installTasks.py
# required to establish the addon data directory on install.

import os
from logHandler import log

def onInstall():

	userPath= os.path.expanduser('~')
	addon_data_path= os.path.join(userPath, "linkLibrary-addonFiles")
	if not os.path.exists(addon_data_path):
		try:
			os.mkdir(addon_data_path)
			#create one file in the directory named general.pickle
			open(os.path.join(addon_data_path, "general.pickle"), 'w').close()
		except Exception as e:
			raise e