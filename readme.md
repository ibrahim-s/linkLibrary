# Link Library #

Author: Ibrahim Hamadeh  
Download [Version 2.2.2][1]  
NVDA compatibility: 2021.1 and beyond  

This addon helps the user to arrange his links or bookmarks in library like way.  
From the main dialog of libraries, you can add, rename or remove any existing one  
Got already libraries, then choose the library or category you like and press enter on it.  
On the opened dialog, you will have all links in that category in a list and have access to source url an the about info of each llink if present.  
This addon does not come with a default or assigned gesture or shortcut to it  
You can as always add a gesture or change the existed one going to :  
NVDA menu>preferences>inputGestures>Link Library.  

## Usage ##

*	After assigning a gesture to the addon, using that gesture or shortcut you can open the main dialog of the addon  
*	A dialog will open, listing all libraries or categories of links that are found.  
*	At first no libraries found, it is empty, ready to host the libraries you wish to establish  .  
*	Tabing on that dialog, you can rename, remove, or add any libraries or category of links you want at any time.  
*	Having some libraries, On the list of libraries, stand on one of your choice, and press enter.   
*	A dialog for that library will open, showing all links in it, if any is present(name or label of links) in a list .  
*	At first the library is empty, and no links in it.  
*	We press the context menu (shift + F10), or popup menu, or the
application key, to add a link by entering the url, label and optionaly the about of the link.  
*	Standing on any link in this list, pressing enter on it will open it with the default browser.  
*	Tabing on that dialog you can access the about of the link(some information about the link ) if present, a button to show the source url, another button that gives you the option to open the link with several browsers if found on your computer.  
*	And using the filter control there, you can filter the links that contain specific words or phrases in the library.
*	Stand on the link you want in this list, and press the context menu.  
*	From there you can add, edit, move link to another library, remove that link or all.  
*	Now do you want to import a json library, or export any library as json or html file, Yes you can  
*	For instance to export a library, stand on the library you want to export and press the contact menu, arrow down once to Export library as, choose the type of file you want to be exported, json or html and press enter.  
*	A dialog will open to choose the folder you want to export to, choose folder and press enter or navigate to select folder button and press on it.  
*	That's it, an information message will be displayed telling you that the library has been exported, congratulations.  
*	Another  beautiful thing, if you export a library as html, you can if you want include the links in that file in firefox bookmarks.  
*	Just open firefox, from the bookmarks menu choose show all bookmarks control+shift+b.  
*	In the menu of the new window, go to Import and Backup submenu, then to Import Bookmarks from HTML… and press enter.  
*	Navigate through the dialog opened to the html file and select it. After that an entry or folder having the same name of the imported library will be found in the firefox bookmarks menu including all links of the imported library in it.  
*	Lastly mentioned, but may be most important, is that you got the ability to choose the place of data files of your addon.  
*	First upon installing the addon, a message box will appear asking you if yo agree to create the folder that hosts the data files for the addon in your home user directory.  
*	you can if you wish, press cancel and choose the directory required to host data files later from the settings dialog of the addon in preferences menu.  
*	Go to NVDA menu>Preferences> Link Library> Link Library Setting..., and open settings dialog.  
*	You can by "Add new path" button, add one or more paths, or remove, by remove button, any of the paths you have added.
*	After choosing the new default path, for data files or libraries for the addon in that dialog  
*	If you want to make it perminant, you have to save settings pressing control+nvda+c, especially if your settings is not set to save on exit in general settings dialog.  
*	Worth noting that creating the folder to host the data files in the home user directory, helps that all instances of the addon on the computer can share the same files or data base  
*	and choosing another path like dropbox for example, will give the user the ability to share the same folder or data base with instances of the addon on another computer that uses the same dropbox account.  

## Sub library feature ##

You can add if you like sub libraries to any library.

*	open the library you want
*	Press the context or popup or application menu
*	Great, now you have from there the option to add, and remame or remove any sub libraries if they are present.
Easy , isn't it, enjoy!

## Add a link on the fly ##

Wonderful feature: Add link of web page on the fly

To use this feature, first you have to assign a gesture or shortcut to it , by going to: NVDA menu(NVDA+N)/preferences/Input gestures/Link Library/Add the link and title of web page on the fly to library you choose.

Now while browsing the net, if you like to add a page to any library in Link library addon you can do that. From any place on the page you like, press the gesture or shortcut for this feature, a window will open saying "Add link and title of web page to library", In it a button saying "Choose library:", press the button, and from the popup menu displayed choose the library you like and press enter.

That's it , the link or url of the web page is added to library, with it's title as label, and you will hear a confirmation message telling you that. beautiful thing really.

### Changes for 2.2.2 ###

*	Now, it is possible to export a library with it's sublibraries as html file, and then if you wish, integrate it into firefox bookmarks.

### Changes for 2.2.1 ###

*	Update addon template files, and use github actions to build the addon instead of apveyor.

### Changes for 2.2 ###

*	Fix a slight bug, in extracting the title of web page, in Add a link on the fly feature.

### Changes for 2.1.9 ###

*	Make possible to add a link of web page on the fly, assign a gesture to this feature, and on any page press it, from the popup menu Choose the library,and the link will be added, with title of page as label.

### Changes for 2.1.8 ###

*	Add the option to open the link in private mode for firefox, Chrome and Edge, and you can access that after pressing the "Open link with" button  in link dialog.

### Changes for 2.1.6 ###

*	UpdateTurkish translation by Umut KORKMAZ.

### Changes for 2.1.5 ###

*	Make "Has sub library" and "Sub library" translatable strings.
*	It is now possible to remove a library with sub libraries, it was a bug fixed, reported by Umut KORKMAZ
*	when trying to remove a library that has sub libraries in it, now the message will warn you that you are going to remove a library with it's sub libraries, to be clear about that.

### Changes for 2.1.4 ###

*	Add sub library feature, the user now can add to a library a sub library, rename or remove it.

### Changes for 2.1.3 ###

*	Add Yandex browser to the list of browsers, that you can open the link with. Thanks to the user who requested that.

### Changes for 2.1.2 ###

*	Add Russian localization, by Kostenkov-2021
*	Update Ukrainian translation, by VovaMobile.

### Changes for 2.1.1 ###

*	Update last tested version, so now the addon is compatible with NVDA 2024.1.

### Changes for 2.1 ###

*	Make a combo box in setting dialog of the addon, to choose an action after activating a link, instead of a checkbox.  
now you can choose either: Do nothing or Close the library window only, or Close the main window of the addon after activating a link.
*	Now the title of main window of the addon, does not include the whole path of data files, but only parent directory.  
If your data folder for example in document folder, the title will no longer be:  
"Link Library - C:\users\...\Documents". and instead it will be:
"Link Library - Documents".

### Changes for 2.0 ###

*	Add Simple Chinease locale.

### Changes for 1.9 ###

*	Update last tested version, making the addon compatible with NVDA 2023.1.

### Changes for 1.8 ###

*	Add a filter control in the dialog of each library, using it the user now can filter links in the library which only contain specific words or phrases, either in the url or label of the link.
*	In the main dialog of libraries, after adding or renaming library, the list of libraries is arrange now alphabaticaly, and that was missing before.

### Changes for 1.7 ###

*	Add Portuguese translation for the addon.

### Changes for 1.6 ###

*	Add Ukrainian translation.

### Changes for 1.5 ###

*	Now you can move a link from one library to another, and this can be achieved through popup menu, then Move link to menu item, then from the submenu there you can choose the library and press enter on it.

### Changes for 1.4 ###

*	Now when closing an opened library, by the escape key or Cancel button  
The focus will return back to the main window of libraries.

### Changes for 1.3 ###

*	Replace close button by OK and Cancel in link dialog, and make possible to remove general library in library dialog.  
*	Change minimum tested version of the addon to 2019.3.  
*	Add Turkish translation for the addon.  

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

### Contributions ###

Very grateful for:
*	Umut KORKMAZ, for supporting the Turkish translation for the addon.
*	VovaMobile , for supporting the Ukrainian translation for the addon.

### contact me ###

In the case of any bugs or suggestion you can [send me an email.](mailto:ibra.hamadeh@hotmail.com)

[1]: https://github.com/ibrahim-s/linkLibrary/releases/download/2.2.2/linkLibrary-2.2.2.nvda-addon
