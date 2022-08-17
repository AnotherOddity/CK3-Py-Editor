import pathlib
import tkinter as tk
import tkinter.filedialog
from sys import exit as safeExit

from Ck3PyModules import find_ck3

def ask_user_ck3_dir():
    #This asks the user to locate the vanilla CK3 game files.
    while True:
        strRootDir = tk.filedialog.askdirectory(
            mustexist=True,
            title='Please select CK3 installation folder'
        )
        print('Checking...')
        if strRootDir[-24:] == '/Crusader Kings III/game':
            print(strRootDir)
            break
        elif strRootDir[-19:] == '/Crusader Kings III':
            print(strRootDir)
            print('...adding /game')
            strRootDir += '/game'
            print(strRootDir)
            break
        else:
            print('Error! Path: '+strRootDir)
            retryQuery = tk.messagebox.askretrycancel(
                title='Error!',
                message='That folder doesn\'t look like the CK3 directory. Do you want to try again?'
            )
            if retryQuery == False:
                print('Cancelling...')
                root.destroy() #Ensuring the tkinter root window is actually closed.
                safeExit('Exiting program...')
    return pathlib.Path(strRootDir)

def doSearch():
    charDir = pathlib.PurePath(pathRootDir).joinpath('history', 'characters')
    print(charDir)
    fileName = file_entry.get()
    if not fileName.endswith(".txt"):
        fileName += ".txt"
    testFile = charDir.joinpath(fileName)
    print(testFile)
    print('\n\n')
    queryList = query_entry.get().split()
    # TODO: instead of printing the results, put them in the result_view
    # with result_view.set()
    with open(testFile) as f:
        fileSearchCK3(f, 0, *queryList)

def build_file_entry(parent):
    label = tk.Label(parent, text="File to search:")
    entry = tk.Entry(parent)
    label.pack()
    entry.pack()
    return entry

def build_query_entry(parent):
    label = tk.Label(parent, text="Query string:")
    entry = tk.Entry(parent)
    label.pack()
    entry.pack()
    return entry

def build_search_button(parent):
    button = tk.Button(parent, text="Search", command=doSearch)
    button.pack()
    return button

def build_result_view(parent):
    var = tk.StringVar()
    view = tk.Label(parent, height=20, textvariable=var)
    view.pack()
    return var

#Initialising a tkinter root window.
root = tk.Tk()
root.withdraw() #Hiding, but not closing, the root window.
root.attributes('-topmost', True)

pathRootDir = None
try:
    pathRootDir = find_ck3.find_ck3_game_directory()
except:
    pass
if pathRootDir is None:
    pathRootDir = ask_user_ck3_dir()

print('Checking path...')
print(pathRootDir)
#For me, this should return:
#F:\SteamLibrary\steamapps\common\Crusader Kings III\game



'''
#This 'walks down' and records all files and folders within a base folder.
#This includes any files and folders within folders inside the base folder (and so on).
#It does NOT record any directories specified by "excludes", and will pretend they don't exist.
#"excludes" is an optional argument, it defaults to being empty, but otherwise should be a list.
#Folders are recorded as lists, the first (list[0]) item being the folder name, the rest being their contents.

def walkDownDir(directory, excludes = list()):
    items = list((directory.parts[-1],))
    for child in directory.iterdir():
        if child.is_dir():
            if child not in excludes:
                items.append(walkDownDir(child))
        else:
            items.append(child.parts[-1])
    return items

#Just a little printing of the contents.
contents = walkDownDir(pathRootDir)

#for i in range(len(contents)):
#    print(contents[i])

def printDir(directory):
    for i in range(len(directory)):
        if isinstance(directory[i], list):
            print(directory[i][0])
        else:
            print(directory[i])

currentDir = contents

while True:
    printDir(currentDir)
    queryContinue = input('Would you like to navigate the directory? Y/N:  ')
    if queryContinue == 'N':
        safeExit('Goodbye...')
    else:
        queryType = input('Would you like to search this folder? Y/N:  ')
        if queryType == 'Y':
            queryFolder = input('Please enter an item to search for:  ')
            for i in range(len(currentDir)):
                if isinstance(currentDir[i], list) and currentDir[i][0] == queryFolder:
                    print('Folder found!')
                    currentDir = currentDir[i]
                    break
                elif currentDir[i] == queryFolder:
                    print('File found!')
                    print(currentDir[i])
                    print('')
                    break
        else:
            queryParent = input('Would you like to go to return to the start? Y/N:  ')
            if queryParent == 'Y':
                currentDir = contents
'''

def fileSearchCK3(file, logicType, *query):
    currentEntry = []
    selectedEntries = []
    ofInterest = []
    for i in range(len(query)):
        ofInterest.append(False)
    curlyBraces = 0
    for line in file:
        for j in range(len(query)):
            if query[j] in line:
                ofInterest[j] = True
        if '{' in line:
            curlyBraces += 1
        if curlyBraces != 0:
            currentEntry.append(line)
        if '}' in line:
            curlyBraces += -1
            if curlyBraces == 0:
                if all(ofInterest) and logicType == 0: #AND
                    selectedEntries.append(currentEntry)
                    for k in range(len(ofInterest)):
                        ofInterest[k] = False
                elif any(ofInterest) and logicType == 1: #OR
                    selectedEntries.append(currentEntry)
                    for k in range(len(ofInterest)):
                        ofInterest[k] = False
                #elif not any(ofInterest)) and logicType == 2: #NOR
                #    selectedEntries.append(currentEntry)
                #    for k in range(len(ofInterest)):
                #        ofInterest[k] = False
                #    NOR IS PRESENTLY NOT FUNCTIONING
                currentEntry = []
    else:
        print('CHECKPOINT!\n\n')
        for i in selectedEntries:
            for j in i:
                print(j.rstrip('\n'))
            print('\n\n')


file_entry = build_file_entry(root)
query_entry = build_query_entry(root)
search_button = build_search_button(root)
result_view = build_result_view(root)
root.deiconify()
root.mainloop()
