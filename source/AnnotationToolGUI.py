#Dieses Anwendung nimmt automatische Annotationen im TEI XML Standard vor.
#Autor: Benjamin Spendrin
#Email: benjamin.spendrin@posteo.de

#ToDo
#Dateipfade eingeben statt hard codiert
#Sanity Checks --> Gucken, dass Tag nicht schon vorhanden
#Ausgabe, wenn sowas passiert?
#Fehlerausgaben
#Ganz weit weg: simple GUI, mit Eingabe der Tags?

from __future__ import annotations
from distutils.filelist import FileList
from textwrap import wrap
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import Grid
from tkinter import filedialog

import os

def close_window():
    mainWindow.destroy()

def openFile():
    name = filedialog.askopenfilename() 
    #print(name)
    return name

#Funktionen, um die Pfade für die Dateiliste und die Tagliste auszuwählen
def setDateilistePfad():
    global FileListPath
    FileListPath = os.path.abspath(openFile())
    with open(FileListPath, 'r', encoding = "utf8") as f:
        DateiListe.insert(INSERT, f.read())
        DateiListe.config(state = DISABLED)
    labDateiListenPfad.config(text = FileListPath)


def setWordListPath():
    global WordListPath
    WordListPath = os.path.abspath(openFile())
    with open(WordListPath, 'r', encoding = "utf8") as f:
        TagListe.insert(INSERT, f.read())
        TagListe.config(state = DISABLED)
    labWordListPath.config(text = WordListPath)


def setSourceFolder():
    global sourceFolderPath
    sourceFolderPath = filedialog.askdirectory()
    #print("Source Folder: " + sourceFolderPath)
    labSourceFolder.config(text = sourceFolderPath)


def setDestinationFolder():
    global destinationFolderPath
    destinationFolderPath = filedialog.askdirectory()
    #print("Destination Folder: " + destinationFolderPath)
    labDestinationFolder.config(text = destinationFolderPath)


def printFileList():
    with open(FileListPath, 'r', encoding = "utf8") as f:
        DateiListe.insert(INSERT, f.read())
        DateiListe.config(state = DISABLED)
    

#Text aus Tag-Liste einfügen
def printWordList():
    with open(WordListPath, 'r', encoding = "utf8") as f:
        TagListe.insert(INSERT, f.read())
        TagListe.config(state = DISABLED)

def annotationStarten(FileListPath, WordListPath, destinationFolderPath, sourceFolderPath):
    #print("Starting annotation:")
    #print("FileListPath: " + FileListPath)
    #print("WordListPath: " + WordListPath)
    #print("SrcPath: " + sourceFolderPath)
    #print("DestPath: " + destinationFolderPath)

    ###########################################################
    #Backups anlegen
    def BackupXML(ListFilename):
        import shutil #Bibliothek zum Dateien kopieren
        fileList = open(ListFilename, 'r', encoding = "utf8").read().splitlines()
        for line in fileList:
            shutil.copyfile((line+".xml"),(line+".xml.backup"))
    ###########################################################

    ###########################################################
    #Backups einspielen (nur fürs Testen)
    def restoreXMLBackups(ListFilename):
        import shutil #Bibliothek zum Dateien kopieren
        fileList = open(ListFilename, 'r', encoding = "utf8").read().splitlines()
        for line in fileList:
            shutil.copyfile((line+".xml.backup"),(line+".xml"))
    ###########################################################

    ###########################################################
    #Einlesen von Tags und Wörtern, die getaggt werden sollen
    def readAnnotationData(WordListPath):
        listOfWords = open(WordListPath, 'r', encoding = "utf8").read().splitlines()
    ###########################################################

    import re #Library für RegEx
    #Pfade für Dateien

    #Nur im Testen: Backups wiederherstellen (später Backups anlegen!)
    #restoreXMLBackups(FileListPath)
    #BackupXML(FileListPath)

    #Gehe alle Dateien aus der fileList durch
    fileList = open(FileListPath, 'r', encoding = "utf8").read().splitlines()
    #print(fileList)

    for currFile in fileList:
        # Aktuelle Datei einlesen
        if os.name == "nt":
            with open((sourceFolderPath + "\\" + currFile+".xml"), 'r', encoding = "utf8") as file :
                filedata = file.read()
        elif os.name == "posix":
            #print("Curr File: " + sourceFolderPath  + "/" + currFile + ".xml")
            with open((sourceFolderPath  + "/" + currFile + ".xml"), 'r', encoding = "utf8") as file :
                filedata = file.read()

        # Zeichenkette ersetzen
        ### Einlesen von Tags und Wörtern
        wordList = open(WordListPath, 'r', encoding = "utf8").read().splitlines()
        #Gehe alle Wörter durch
        for currWord in wordList:
            #Wenn aktuelles Wort mit # beginnt, setze aktuelles Tag darauf
            if currWord.startswith("#"):
                currTag = currWord[1:] #Entferne das # (=den 1. char des strings)
            #Wenn nicht, ersetze aktuelles Wort mit dem Tag
            else:
                #Annotiert wird:
                #Wenn das Wort von Leerzeichen angeführt und gefolgt wird
                #a) von einem Leerzeichen
                filedata = filedata.replace(" " + currWord + " ", (" <term key=\"" + currTag + "\">" + currWord + "</term> "))
                #Richtiges Format für die Tags:                <term key="Alkohol">alkoholischer Getränke</term>
                #b) von einem Komma
                filedata = filedata.replace(" " + currWord + ",", (" <term key=\"" + currTag + "\">"+ currWord + "</term>,"))
                #c) von einem Punkt (= Satzende)
                filedata = filedata.replace(" " + currWord + ".", (" <term key=\"" + currTag + "\">"+ currWord + "</term>."))
                #d) von einem Ausrufezeichen
                filedata = filedata.replace(" " + currWord + "!", (" <term key=\"" + currTag + "\">"+ currWord + "</term>!"))
                #e) von einem Fragezeichen
                filedata = filedata.replace(" " + currWord + "?", (" <term key=\"" + currTag + "\">"+ currWord + "</term>?"))
                
        if os.path.exists(destinationFolderPath) == False:
            os.makedirs(destinationFolderPath)
        
        if os.name == "nt":
            with open(destinationFolderPath  + "\\" +  currFile + ".xml", "w", encoding = "utf8") as file:
                file.write(filedata)
                #print("Wrote File: " + destinationFolderPath + "\\" + currFile+ ".xml")
        elif os.name == "posix":
            with open(destinationFolderPath  + "/" +  currFile + ".xml", "w", encoding = "utf8") as file:
                file.write(filedata)
                #print("Wrote File: " + destinationFolderPath + "/" + currFile + ".xml")


#Kreiert Fenster
mainWindow = Tk()
mainWindow.title("Annotations-Tool NsRdMi") #Fenstertitel
mainWindow.geometry("1000x600") #Fenstergröße: Breite x Höhe
mainWindow.minsize(width = 800, height = 800) #Mindestgrößen
#root.maxsize(width = 1000, height = 750) #Maximalgrößen
#mainWindow.resizable(width = False, height = False) #Sperre Veränderbarkeit der Größe

#Scrollbar
S = Scrollbar(mainWindow)

FileListPath = "Keine Dateiliste ausgewählt"
WordListPath = "Keine Tagliste ausgewählt"
sourceFolderPath="Kein Quellordner ausgewählt"
destinationFolderPath="Kein Zielordner ausgewählt"

#Anzeige der ausgewählten Dateien
global labDateiListenPfad
DateiListe = Text(mainWindow)
labDateiListenPfad = tk.Label(mainWindow, text = FileListPath)

global labWordListPath
TagListe = Text(mainWindow)
labWordListPath = tk.Label(mainWindow, text = WordListPath)

BeschreibungAllgemein = tk.Label(mainWindow, text = "Die beiden Spalten zeigen die zu bearbeitenden Dateien links und die zu setzenden Tags und ihre dazugehörigen Signalworte rechts. \n Über die darunterstehenden Buttons können die jeweiligen Dateien sowie der Quell- und Zielordner angegeben werden.", wraplength=800, justify=LEFT)

BeschreibungDateiliste = tk.Label(mainWindow, text = "In diese Liste müssen die zu annotierenden Dateien in einzelnen Zeilen, ohne Dateiendung (d.h. nur die ID) eingetragen werden.", wraplength=400,justify=LEFT)

BeschreibungTagliste = tk.Label(mainWindow, text = "In die Tagliste müssen die Tags und dazugehörigen zu markierenden Worte wie folgt eingetragen werden:\n Das # markiert ein Schlagwort, alle bis zum nächsten # folgenden Worte werden mit diesem Annotiert. Es werden *nur* die angegebenen Schreibweisen annotiert, keine Abwandlungen davon (d.h. Pause != Pausen). Sobald das nächste # folgt, wird ein neues Tag annotiert.", wraplength=400,justify=LEFT)

#Button: Dateiliste auswählen
btnDateiliste = tk.Button(mainWindow, text = "Dateiliste auswählen", command = lambda: [setDateilistePfad()])

#Button: Tagliste auswählen
btnWordList = tk.Button(mainWindow, text = "Tagliste auswählen", command = lambda: [setWordListPath()])

#Button: Quellordner
btnChooseSourceFolder = tk.Button(mainWindow, text = "Quellordner auswählen", command = lambda: [setSourceFolder()])
global labSourceFolder
labSourceFolder = tk.Label(mainWindow, text = sourceFolderPath)


#Button: Zielordner
btnChooseDestinationFolder = tk.Button(mainWindow, text = "Zielordner wählen", command = lambda: [setDestinationFolder()])
global labDestinationFolder
labDestinationFolder = tk.Label(mainWindow, text = destinationFolderPath)

#Button, um die Annotation zu starten
btnAnnotieren = tk.Button(mainWindow, text="Annotation starten", command = lambda: annotationStarten(FileListPath, WordListPath, destinationFolderPath, sourceFolderPath))

#Abbrechen-Button
btnAbbrechen = tk.Button(mainWindow, text="Schließen", command = close_window)



#Grid bauen: jede Spalte bekommt ein Gewicht; so werden sie auf die Breite verteilt
mainWindow.columnconfigure(0, weight = 1)
mainWindow.columnconfigure(1, weight = 1)

BeschreibungAllgemein.grid(column = 0, row = 0, padx=5, pady=5, columnspan=2)

BeschreibungDateiliste.grid(column = 0, row = 1, padx=5, pady=5)
BeschreibungTagliste.grid(column = 1, row = 1, padx=5, pady=5)

DateiListe.grid(column=0, row=2, padx=5, pady=5)
TagListe.grid(column=1, row=2, padx=5, pady=5)

btnDateiliste.grid(column = 0, row = 3)
btnWordList.grid(column = 1, row = 3)

labWordListPath.grid(column=1, row=4, padx=5, pady=5)
labDateiListenPfad.grid(column=0, row=4, padx=5, pady=5)

btnChooseSourceFolder.grid(column = 0, row = 5)
btnChooseDestinationFolder.grid(column = 1, row = 5)

labSourceFolder.grid(column=0, row=6, padx=5, pady=5)
labDestinationFolder.grid(column=1, row=6, padx=5, pady=5)

btnAnnotieren.grid(column=0, row=7)
btnAbbrechen.grid(column=1, row=7)

#Mainloop-Methode --> "Eventloop" --> muss aufgerufen werden --> Endlosschleife, die Interaktionen mit GUI abfängt
mainWindow.mainloop()
#Was hier drunter steht, wird erstmal nicht ausgeführt!!!!