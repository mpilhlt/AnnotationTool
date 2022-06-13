#Dieses Script nimmt automatische Annotationen im TEI XML Standard vor.
#Autor: Benjamin Spendrin
#Email: benjamin.spendrin@posteo.de

#ToDo
#Was passiert, wenn erst PauseN und dann Pause annotiert werden?
#Dateipfade eingeben statt hard codiert
#Sanity Checks --> Gucken, dass Tag nicht schon vorhanden
#Ausgabe, wenn sowas passiert?
#Fehlerausgaben
#Ganz weit weg: simple GUI, mit Eingabe der Tags?

###########################################################
#Backups anlegen
def BackupXML(ListFilename):
    import shutil #Bibliothek zum Dateien kopieren
    fileList = open(ListFilename, 'r').read().splitlines()
    for line in fileList:
        shutil.copyfile((line+".xml"),(line+".xml.backup"))
###########################################################

###########################################################
#Backups einspielen (nur fürs Testen)
def restoreXMLBackups(ListFilename):
    import shutil #Bibliothek zum Dateien kopieren
    fileList = open(ListFilename, 'r').read().splitlines()
    for line in fileList:
        shutil.copyfile((line+".xml.backup"),(line+".xml"))
###########################################################

###########################################################
#Einlesen von Tags und Wörtern, die getaggt werden sollen
def readAnnotationData(WordListPath):
    listOfWords = open(WordListPath, 'r').read().splitlines()
###########################################################

###########################################################
###########################################################
###########################################################

import re #Library für RegEx
import os


#Pfade für Dateien
workingDir = "./"
ListFilename = "./fileList.txt"
WordListPath = "./wordList.txt"
SpeicherortPath="./annotierteDateien/"
#Nur im Testen: Backups wiederherstellen (später Backups anlegen!)
#restoreXMLBackups(ListFilename)
#BackupXML(ListFilename)

#Gehe alle Dateien aus der fileList durch
fileList = open(ListFilename, 'r').read().splitlines()
#print(fileList)

for currFile in fileList:

    # Aktuelle Datei einlesen
    with open((workingDir+currFile+".xml"), 'r') as file :
        filedata = file.read()
        print("Opening File: " + currFile + ".xml")

    # Zeichenkette ersetzen
    ### Einlesen von Tags und Wörtern
    wordList = open(WordListPath, 'r').read().splitlines()

    #Gehe alle Wörter durch
    for currWord in wordList:
        #Wenn aktuelles Wort mit # beginnt, setze aktuelles Tag darauf
        if currWord.startswith("#"):
            currTag = currWord[1:] #Entferne das # (=den 1. char des strings)
            print("Current Tag: " + currTag)
        else:
            #Annotiert wird:
            #Wenn das Wort von Leerzeichen angeführt und gefolgt wird
            #a) von einem Leerzeichen
            filedata = filedata.replace(" " + currWord + " ", (" <term key=" + currTag + ">"+ currWord + "</term> "))
            #b) von einem Komma
            filedata = filedata.replace(" " + currWord + ",", (" <term key=" + currTag + ">"+ currWord + "</term>,"))
            #c) von einem Punkt (= Satzende)
            filedata = filedata.replace(" " + currWord + ".", (" <term key=" + currTag + ">"+ currWord + "</term>."))
            #d) von einem Ausrufezeichen
            filedata = filedata.replace(" " + currWord + "!", (" <term key=" + currTag + ">"+ currWord + "</term>!"))
            #e) von einem Fragezeichen
            filedata = filedata.replace(" " + currWord + "?", (" <term key=" + currTag + ">"+ currWord + "</term>?"))


 #           {\b\w*(Paus)\w*\b}
            #aktueller RegEx, nach der gesucht werden soll: Optionen r (kein Escape bei \; f --> Variable kann in {} stehen
            #currRegEx = f'\b\w*({currWord})\w*\b'


            #aktueller String, der eingesetzt werden soll (= mit dem Tag)
            #currRepString = "<term key=" + currTag + ">"+ currWord + "</term>"
#            currRepString = "</term>"

#            print("Current Word: " + currWord)
#            print("CurrRegEx: " + f'\b\w*({currWord})\w*\b')
#            print("Curr RepString: \n" + currRepString)
            #filedata = re.sub(currWord, currRepString, filedata)
            #filedata = re.sub(currRegEx, "<term key=" + currTag + ">" + r"\1" + "<\term>", filedata, flags=re.IGNORECASE)

    # Datei schreiben
    if os.path.exists(SpeicherortPath) == False:
        os.makedirs(SpeicherortPath)

    with open(SpeicherortPath + currFile + ".xml", "w") as file:
        file.write(filedata)
        print("Wrote File: " + SpeicherortPath+currFile+".xml")