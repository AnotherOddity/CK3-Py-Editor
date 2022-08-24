import pathlib
import tkinter as tk
from tkinter import ttk
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
    queryList = []
    for entry in query_entries:
        query = entry.get()
        if query:
            queryList.append(query)
    logicType = match_var.get()
    with open(testFile) as f:
        text = fileSearchCK3(f, logicType, *queryList)
    if text is None or not text:
        text = "None found."
    result_var.set(text)
    result_view.configure(height=len(text.splitlines()))

def build_file_entry(parent):
    label = tk.Label(parent, text="File to search:")
    entry = tk.Entry(parent)
    label.pack()
    entry.pack()
    return entry

def build_query_entries(parent):
    entries = []
    for i in range(1, 4):
        label = tk.Label(parent, text="Query string %d:" % i)
        entry = tk.Entry(parent)
        label.pack()
        entry.pack()
        entries.append(entry)
    var = tk.IntVar()
    buttons = tk.Frame(parent)
    button1 = tk.Radiobutton(buttons, text="Match any", variable=var, value=1)
    button2 = tk.Radiobutton(buttons, text="Match all", variable=var, value=0)
    button1.pack(side = tk.LEFT)
    button2.pack(side = tk.RIGHT)
    buttons.pack()
    return entries, var

def build_search_button(parent):
    button = tk.Button(parent, text="Search", command=doSearch)
    button.pack()
    return button

def build_result_view(parent):
    # tutorial https://blog.teclado.com/tkinter-scrollable-frames/
    container = ttk.Frame(parent)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    var = tk.StringVar()
    view = tk.Label(scrollable_frame, height=20, width=80, textvariable=var, anchor='nw', justify="left")
    view.pack(side="left")

    container.pack()
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return (var, view)

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
        outtext = ""
        for i in selectedEntries:
            for j in i:
                outtext += j.replace('\t', '        ')
                print(j.rstrip('\n'))
            outtext += '\n\n'
            print('\n\n')
        return outtext


file_entry = build_file_entry(root)
query_entries, match_var = build_query_entries(root)
search_button = build_search_button(root)
result_var, result_view = build_result_view(root)
root.deiconify()
root.mainloop()
