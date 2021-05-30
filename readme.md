# Link Library #

Author: Ibrahim Hamadeh  
Download [Version 1.2][1]  
NVDA compatibility: 2018.3 and beyond  
Python compatibility: Python2 and Python3  

This addon helps the user to arrange his links or bookmarks in library like way.  
From the main dialog of libraries, you can choose the library or category you like and press enter on it.  
On the opened dialog, you will have all links in that category in a list and have access to source url an the about info of each llink if present.  
This addon does not come with a default or assigned gesture or shortcut to it  
You can as always add a gesture or change the existed one going to :  
NVDA menu>preferences>inputGestures>Link Library.  

## Usage ##

*	After assigning a gesture to the addon, using that gesture or shortcut you can open the main dialog of the addon  
*	A dialog will open, listing all libraries or categories of links that are found.  
*	At first only one library named General will be found, it is empty, ready to host general links.  
*	Tabing on that dialog, you can rename, remove, or add any libraries or category of links you want at any time.  
*	On the list of libraries, stand on one of your choice, and press enter.   
*	A dialog for that library will open, showing all links in it, if any is present(name or label of links) in a list .  
*	At first the library is empty, and no links in it.  
*	Press the context menu, to add a link by entering the url, label and optionaly the about of the link.  
*	Standing on any link in this list, pressing enter on it will open it with the default browser.  
*	Tabing on that dialog you can access the about of the link(some information about the link ) if present, a button to show the source url, another button that gives you the option to open the link with several browsers if found on your computer.  
*	Stand on the link you want in this list, and press the context menu.  
*	From there you can add, edit, remove that link or all.  
*	Now do you want to import a json library, or export any library as json or html file, Yes you can  
*	For instance to export a library, stand on the library you want to export and press the contact menu, arrow down once to Export library as, choose the type of file you want to be exported, json or html and press enter.  
*	A dialog will open to choose the folder you want to export to, choose folder and press enter or navigate to select folder button and press on it.  
*	That's it, an information message will be displayed telling you that the library has been exported, congratulations.  
*	Another  beautiful thing, if you export a library as html, you can if you want include the links in that file in firefox bookmarks.  
*	Just open firefox, from the bookmarks menu choose show all bookmarks control+shift+b.  
*	In the menu of the new window, go to Import and Backup submenu, then to Import Bookmarks from HTML… and press enter.  
*	Navigate through the dialog opened to the html file and select it. After that an entry or folder having the same name of the imported library will be found in the firefox bookmarks menu including all links of the imported library in it.  
*	Lastly mentioned, but may be most important is that you got the ability to choose the place of data files of your addon.  
*	First upon installing the addon, a message box will appear asking you if yo agree to create the folder that hosts the data files for the addon in your home user directory.  
*	you can if you wish, press cancel and choose the directory required to host data files later from the settings dialog of the addon in preferences menu.  
*	Afterchoosing the new default path for data files from the addon settings in preferences menu  
*	If you want to make it perminant, you have to save settings pressing control+nvda+c, especially if your settings is not put to save on exit in general settings dialog.  
*	Worth noting that creating the folder to host the data files in the home user directory, helps that all instances of the addon on the computer can share the same files or data base  
*	and choosing another path like dropbox for example, will give the user the ability to share the same folder or data base with instances of the addon on another computer that uses the same dropbox account.  

### Changes for 1.2 ###

*	Fixing a bug activating context menu in NVDA 2021.1 api.  
*	Removing edge legacy from open link with in link dialog.  

### Changes for 1.1 ###

*	Now links in libraries, that is to say their labels are sorted ignoring case sensetivity.  
*	During importing a json library, now if similar name exists  
the user will be asked if he wishes to merge the two libraries or not, if he says No, the library will be imported having a number between paranthesis as suffix denoting number of similar libraries  
and if he wants to merge the libraries, the imported or existed file will have the two dictionaries merged inside it.  

### Changes for 1.0 ###

*	Change Data or library files from .pickle to .json files
*	In the title of link library dialog, now the label of the path chosen by the user to store data files, is now appended to the title.  

### Changes for 0.5 ###

*	Add dialog in the addon settings dialog to let the user add or choose the directory that he wishes to host the data file of the addon.  
*	So now he can keep on the default path which is the home user directory, or choose from the settings dialog the path he wants.  

### Changes for 0.4 ###

*	Make the addon python3 compatible  

### Changes for 0.2 ###

*	Make the only place to save and retreave data, a folder named "linkLibrary-addonFiles" in the home user directory. So that it will be used by all instances of the addon in installed or portable versions of NVDA.

### Changes for 0.1 ###

*	Initial version.

### contact me ###

In the case of any bugs or suggestion you can [send me an email.](mailto:ibra.hamadeh@hotmail.com)

[1]: https://github.com/ibrahim-s/linkLibrary/releases/download/1.2/linkLibrary-1.2.nvda-addon