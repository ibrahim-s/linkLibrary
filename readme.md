# Link Library #

Author: Ibrahim Hamadeh  
Download [Development version 0.2][1]  

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
*	A dialog for that library will open, showing all linksin it (name or label of links) in a list .  
*	Standing on any link in this list, pressing enter on it will open it with the default browser.  
*	Tabing on that dialog you can access the about of the link(some information about the link ) if present, a button to show the source url, another button that gives you the option to open the link with several browsers if found on your computer.  
*	Stand on the link you want in this dialog, and press the context menu.  
*	From there you can add, edit, remove that link or all.  
*	Now do you want to import a pickled library, or export any library as pickle or html file, Yes you can  
*	For instance to export a library, stand on the library you want to export and press the contact menu, arrow down once to Export library as, choose the type of file you want to be exported, pickle or html and press enter.  
*	A dialog will open to choose the folder you want to export to, choose folder and press enter or navigate to select folder button and press on it.  
*	That's it, an information message will be displayed telling you that the library has been exported, congratulations.  
*	A last and beautiful thing, if you export a library as html, you can if you want include the links in that file in firefox bookmarks.  
*	Just open firefox, from the bookmarks menu choose show all bookmarks control+shift+b.  
*	In the menu of the new window, go to Import and Backup submenu, then to Import Bookmarks from HTML… and press enter.  
*	Navigate through the dialog opened to the html file and select it. After that an entry or folder having the same name of the imported library will be found in the firefox bookmarks menu including all links of the imported library in it.  

### Changes for 0.2 ###

*	Make the only place to save and retreave data, a folder named "linkLibrary-addonFiles" in the home user directory. So that it will be used by all instances of the addon in installed or portable versions of NVDA.

### Changes for 0.1 ###

*	Initial version.

### contact me ###

In the case of any bugs or suggestion you can [send me an email.](mailto:ibra.hamadeh@hotmail.com)

[1]: https://github.com/ibrahim-s/linkLibrary/releases/download/v0.2-dev/linkLibrary-0.2-dev.nvda-addon